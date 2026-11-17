#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="default"
arch="arm64"
app_config=""
archive=""
while (( $# )); do
  case "$1" in
    --extended)
      [[ "$mode" == "default" ]] || { echo "--extended repeated" >&2; exit 2; }
      mode="extended" ;;
    --arch)
      shift
      [[ $# -gt 0 ]] || { echo "--arch needs arm64 or amd64" >&2; exit 2; }
      [[ "$1" == "arm64" || "$1" == "amd64" ]] || { echo "--arch needs arm64 or amd64" >&2; exit 2; }
      arch="$1" ;;
    --app-config)
      shift
      [[ $# -gt 0 && -z "$app_config" ]] || { echo "--app-config needs one file" >&2; exit 2; }
      app_config="$1" ;;
    --*)
      echo "Usage: $0 [--arch arm64|amd64] [--extended] [--app-config fictional-outputs.json] [source-archive.zip]" >&2
      exit 2 ;;
    *)
      [[ -z "$archive" ]] || { echo "Only one source archive may be supplied" >&2; exit 2; }
      archive="$1" ;;
  esac
  shift
done
archive="${archive:-$repo_root/artifacts/aws-amplify-lab-source.zip}"
review_dir="$repo_root/artifacts/linux-verification"
image_name="amplify-companion-linux:local"

test -f "$archive" || { echo "Source archive missing: $archive" >&2; exit 2; }
mkdir -p "$review_dir/scripts" "$review_dir/artifacts"
cp "$repo_root/scripts/check-packaged-companion.py" "$review_dir/scripts/check-packaged-companion.py"
cp "$archive" "$review_dir/artifacts/aws-amplify-lab-source.zip"

docker build --platform "linux/$arch" \
  -f "$repo_root/infra/linux-companion/Dockerfile" \
  -t "$image_name" "$repo_root/infra/linux-companion"
if [[ "$mode" == "extended" ]]; then
  build_dir="$review_dir/full-build"
  mkdir -p "$build_dir"
  cp "$repo_root/architectures/reliable-workflows/requirements-dev.txt" "$build_dir/domain.txt"
  cp "$repo_root/examples/analytics-query/requirements.txt" "$build_dir/analytics.txt"
  docker build --platform "linux/$arch" \
    -f "$repo_root/infra/linux-companion/Dockerfile.extended" \
    -t amplify-companion-linux-extended:local "$build_dir"
  image_name="amplify-companion-linux-extended:local"
fi
docker image inspect "$image_name" --format 'Linux check image: {{.Id}}'
extra_args=()
if [[ "$arch" == "amd64" ]]; then
  # Emulation on an ARM host can make the same offline checks exceed five minutes.
  extra_args+=(--check-timeout 1200)
fi
network_args=(--network none)
memory_limit=2g
if [[ "$mode" == "extended" ]]; then
  extra_args+=(--domain-python /opt/domain/bin/python --analytics-python /opt/analytics/bin/python)
fi
if [[ -n "$app_config" ]]; then
  test -f "$app_config" || { echo "App configuration missing: $app_config" >&2; exit 2; }
  cp "$app_config" "$review_dir/app-config.json"
  extra_args+=(--app-config /work/app-config.json)
  network_args=(--network bridge)
  memory_limit=4g
  mode="$mode-app"
fi
run_status=0
docker run --rm --platform "linux/$arch" "${network_args[@]}" \
  --memory "$memory_limit" --cpus 2 --security-opt no-new-privileges --cap-drop ALL \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --env AWS_CONFIG_FILE=/work/empty-aws-config \
  --env AWS_SHARED_CREDENTIALS_FILE=/work/empty-aws-credentials \
  --env AWS_EC2_METADATA_DISABLED=true \
  -v "$review_dir:/work" "$image_name" \
  python scripts/check-packaged-companion.py --archive artifacts/aws-amplify-lab-source.zip "${extra_args[@]}" || run_status=$?
cp "$review_dir/artifacts/package-checks.json" "$review_dir/artifacts/$mode-package-checks.json"
cp "$review_dir/artifacts/package-checks.json" "$review_dir/artifacts/$mode-$arch-package-checks.json"
echo "Retained Linux report: $review_dir/artifacts/package-checks.json"
exit "$run_status"

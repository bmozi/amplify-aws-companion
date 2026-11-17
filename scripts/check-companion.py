"""Run cloud-free companion checks; use a scoped set in a lab-only packet."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote
from local_only_links import documented_local_only

BASE=Path(__file__).resolve().parents[1]
LABS=['data-contract','local-operations','network-diagnostics','segmentation-contract','recovery-reconciliation','recovery-automation','recovery-critical-path','customer-signals','pipeline-testing','account-onboarding','fleet-maintenance','scaling-policy-model','reliability-growth','performance-boundary-review','monitoring-automation','alarm-diagnostic-runbook','incident-event-workflow','configuration-change-control','security-audit-evidence','agent-tool-boundary','three-tier-boundary','clinic-offline-intake',
      'terraform-lifecycle','governed-delivery','reusable-module','ownership-handoff','file-intake','tenant-isolation','tenant-entitlement','tenant-offboarding','tenant-fairness','migration-cutover','migration-mechanisms','approval-workflow','environment-boundary','event-reconciliation','fleet-ingress','authorized-retrieval','request-telemetry','credential-rotation','tls-boundaries','certificate-endpoint-change','cache-consistency','in-memory-authority','cold-cache-burst','query-plans','canary-release','database-capacity','relational-capacity','network-growth','checkpoint-recovery','search-index','connection-pool','admission-control','bulkhead-capacity','schema-compatibility','reservation-holds','dashboard-grain','telemetry-design','security-finding-review','queue-recovery','api-contract','business-transfer','media-publication','storage-cost','network-cost-routing','network-workload-review','network-bandwidth-selection','arrival-shape','quota-race']
LABS.append('layered-request-boundary')
LABS.append('ebs-volume-economics')
LABS.append('ebs-az-recovery')


def run_lab_only(source_basis, sources, expanded=False):
    """Check selected local labs after verifying every packaged source byte."""
    commands = [
        ('reader_budget_decision', [sys.executable, 'examples/costs/reader-budget-decision/lab.py']),
        ('reader_budget_tests', [sys.executable, '-m', 'unittest', 'discover',
                                 '-s', 'examples/costs/reader-budget-decision', '-p', 'test_*.py']),
        ('oidc_trust_tests', [sys.executable, '-m', 'unittest', 'discover',
                              '-s', 'examples/oidc-trust-boundary', '-p', 'test_*.py']),
        ('global_web_tests', [sys.executable, '-m', 'unittest', 'discover',
                              '-s', 'examples/global-web', '-p', 'test_*.py']),
    ]
    if expanded:
        commands.extend((name, [sys.executable, f'examples/{name}/lab.py'])
                        for name in LABS)
        commands.append(('ipam_governance', [sys.executable, 'examples/ipam-governance/plan.py']))
        commands.append(('ipam_governance_tests', [sys.executable, '-m', 'unittest', 'discover',
                         '-s', 'examples/ipam-governance', '-p', 'test_*.py']))
        commands.append(('hybrid_container_placement', [sys.executable,
                         'examples/hybrid-container-placement/review.py']))
        commands.append(('hybrid_container_placement_tests', [sys.executable, '-m', 'unittest', 'discover',
                         '-s', 'examples/hybrid-container-placement', '-p', 'test_*.py']))
        commands.append(('cloudformation_change_review_tests', [sys.executable, '-m', 'unittest', 'discover',
                         '-s', 'examples/cloudformation-change-review', '-p', 'test_*.py']))
        commands.append(('search_index_ordered',
                         [sys.executable, 'examples/search-index/ordered_lab.py']))
        commands.append(('search_index_ordered_tests',
                         [sys.executable, '-m', 'unittest', 'discover',
                          '-s', 'examples/search-index', '-p', 'test_ordered_lab.py']))
        commands.append(('media_publication_cache_boundary',
                         [sys.executable, 'examples/media-publication/cache-boundary-lab.py']))
        commands.append(('hybrid_dns_two_directions',
                         [sys.executable, 'examples/hybrid-design/dns_path_lab.py']))
    report = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'source_basis': source_basis,
              'mode': 'lab_only_expanded' if expanded else 'lab_only_selected_smoke',
              'scope': (f'Four selected cloud-free groups plus {len(LABS)} declared local lab commands, two IPAM governance checks, two hybrid-placement checks and two ordered-search checks'
                        if expanded else 'Four selected cloud-free command groups') +
                       ' after full manifest verification; not the private-source suite, '
                       'every optional dependency, AWS or learner evidence',
              'checks': []}
    with tempfile.TemporaryDirectory(prefix='amplify-check-config-') as temporary:
        empty = Path(temporary) / 'empty'
        empty.write_text('')
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(('AWS_', 'TF_')) and k != 'PYTHONOPTIMIZE'}
        env.update(AWS_CONFIG_FILE=str(empty), AWS_SHARED_CREDENTIALS_FILE=str(empty),
                   AWS_EC2_METADATA_DISABLED='true', AWS_ACCESS_KEY_ID='testing',
                   AWS_SECRET_ACCESS_KEY='testing', AWS_DEFAULT_REGION='us-east-2')
        for name, command in commands:
            try:
                result = subprocess.run(command, cwd=BASE, env=env, text=True,
                                        capture_output=True, timeout=120)
                item = {'name': name, 'status': 'passed' if result.returncode == 0 else 'failed',
                        'exit_code': result.returncode, 'stdout': result.stdout,
                        'stderr': result.stderr}
            except (OSError, subprocess.TimeoutExpired) as error:
                item = {'name': name, 'status': 'failed', 'error': str(error)}
            report['checks'].append(item)
            print(name + ': ' + item['status'], flush=True)
    changed = [name for name, digest in sources.items() if not (BASE / name).is_file()
               or hashlib.sha256((BASE / name).read_bytes()).hexdigest() != digest]
    report['checks'].append({'name': 'source_unchanged',
                             'status': 'failed' if changed else 'passed', 'changed': changed})
    report['all_requested_passed'] = all(c['status'] == 'passed' for c in report['checks'])
    destination = BASE / 'artifacts/companion-checks.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print('Report: ' + str(destination))
    return 0 if report['all_requested_passed'] else 1



def source_snapshot():
    """Bind checks to Git source or a verified packaged manifest before execution."""
    if (BASE/'.git').exists():
        listed=subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z'],cwd=BASE).decode().split('\0')
        return 'git-working-tree', {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                for name in sorted(set(listed)) if name and (BASE/name).is_file()}
    manifest=BASE/'SOURCE-MANIFEST.sha256'
    if not manifest.is_file():
        raise ValueError('No Git checkout or SOURCE-MANIFEST.sha256; use a clone or the packaged source archive')
    sources={}
    for line in manifest.read_text().splitlines():
        digest,separator,name=line.partition('  ')
        relative=Path(name)
        if not separator or not re.fullmatch('[0-9a-f]{64}',digest) or not name or relative.is_absolute() or '..' in relative.parts or name in sources:
            raise ValueError('Invalid or duplicate source-manifest entry')
        target=BASE/relative
        if target.is_symlink() or not target.resolve().is_relative_to(BASE.resolve()) or not target.is_file():
            raise ValueError('Invalid source-manifest path: '+name)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('Source differs from packaged manifest: '+name)
        sources[name]=digest
    if not sources or 'scripts/check-companion.py' not in sources:
        raise ValueError('Source manifest does not include the companion runner')
    return 'verified-archive-manifest',sources


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domain-python',type=Path,help='Python environment containing the pinned Moto test dependencies')
    parser.add_argument('--analytics-python',type=Path,help='Python environment containing pinned DuckDB')
    parser.add_argument('--containers',action='store_true',help='Build and run the real local Docker release drill')
    parser.add_argument('--app-toolchain',action='store_true',help='Check installed app dependency compatibility and build the app; no install or deployment')
    parser.add_argument('--frontend-publisher-toolchain',action='store_true',help='Run two synthetic browser builds using installed frontend publisher dependencies; no install or deployment')
    parser.add_argument('--lab-only', action='store_true', help='Run selected smoke checks for the reduced lab packet')
    parser.add_argument('--lab-only-expanded', action='store_true',
                        help='Run smoke checks and all declared local lab commands in the reduced packet')
    args=parser.parse_args()
    if sys.flags.optimize:raise SystemExit('Run without Python optimization: the teaching labs use assertions')
    try:
        source_basis,sources=source_snapshot()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        raise SystemExit('Source verification failed before running checks: '+str(error))
    reduced_packet = (source_basis == 'verified-archive-manifest' and
                      not (BASE / 'book' / 'units').is_dir())
    if args.lab_only or args.lab_only_expanded or reduced_packet:
        if reduced_packet:
            print('Reduced packet detected: running selected lab-only checks', flush=True)
        return run_lab_only(source_basis, sources, expanded=args.lab_only_expanded)
    if not (BASE / 'book' / 'units').is_dir():
        raise SystemExit('Full source checkout is missing book/units; run an explicit --lab-only check only for a reviewed reduced packet')
    report={'started_utc':datetime.now(timezone.utc).isoformat(),'scope':'local drills, emulated tests if selected, structural checks; no live AWS or learner evidence','checks':[]}
    commands=[('curriculum',[sys.executable,'scripts/check-curriculum.py']),
              ('sap_c03_domain1',[sys.executable,'scripts/check-sap-c03-domain1.py']),
              ('sap_c03_domain2',[sys.executable,'scripts/check-sap-c03-domain2.py']),
              ('sap_c03_domain3',[sys.executable,'scripts/check-sap-c03-domain3.py']),
              ('sap_c03_domain4',[sys.executable,'scripts/check-sap-c03-domain4.py']),
              ('sap_c03_domain5',[sys.executable,'scripts/check-sap-c03-domain5.py']),
              ('sap_c03_gap_queue',[sys.executable,'scripts/check-sap-c03-gap-queue.py']),
              ('shared_cost_allocation',[sys.executable,'examples/costs/shared-cost-allocation/allocation.py']),
              ('shared_cost_allocation_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/shared-cost-allocation','-p','test_*.py','-v']),
              ('agentcore_identity_path',[sys.executable,'examples/agentcore-identity-path/identity_path.py']),
              ('agentcore_identity_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/agentcore-identity-path','-p','test_*.py','-v']),
              ('application_pod_identity',[sys.executable,'examples/application-pod-identity/lab.py']),
              ('application_pod_identity_tests',[sys.executable,'-m','unittest','discover','-s','examples/application-pod-identity','-p','test_*.py','-v']),
              ('dedicated_hsm_decision',[sys.executable,'examples/dedicated-hsm-decision/lab.py']),
              ('dedicated_hsm_decision_tests',[sys.executable,'-m','unittest','discover','-s','examples/dedicated-hsm-decision','-p','test_*.py','-v']),
              ('provider_evidence_packet',[sys.executable,'examples/provider-evidence-packet/packet.py']),
              ('provider_evidence_packet_tests',[sys.executable,'-m','unittest','discover','-s','examples/provider-evidence-packet','-p','test_*.py','-v']),
              ('dual_stack_journey',[sys.executable,'examples/dual-stack-journey/path_lab.py']),
              ('dual_stack_journey_tests',[sys.executable,'-m','unittest','discover','-s','examples/dual-stack-journey','-p','test_*.py','-v']),
              ('realtime_status',[sys.executable,'examples/realtime-status/ledger.py']),
              ('realtime_status_tests',[sys.executable,'-m','unittest','discover','-s','examples/realtime-status','-p','test_*.py','-v']),
              ('policy_as_code_gates',[sys.executable,'examples/policy-as-code-gates/gate.py']),
              ('policy_as_code_gates_tests',[sys.executable,'-m','unittest','discover','-s','examples/policy-as-code-gates','-p','test_*.py','-v']),
              ('ai_operation_signals',[sys.executable,'examples/ai-operation-signals/lab.py']),
              ('ai_operation_signals_tests',[sys.executable,'-m','unittest','discover','-s','examples/ai-operation-signals','-p','test_*.py','-v']),
              ('ai_audit_evidence',[sys.executable,'examples/ai-audit-evidence/lab.py']),
              ('ai_audit_evidence_tests',[sys.executable,'-m','unittest','discover','-s','examples/ai-audit-evidence','-p','test_*.py','-v']),
              ('multi_cluster_recovery',[sys.executable,'examples/multi-cluster-recovery/lab.py']),
              ('multi_cluster_recovery_tests',[sys.executable,'-m','unittest','discover','-s','examples/multi-cluster-recovery','-p','test_*.py','-v']),
              ('ai_inference_routing',[sys.executable,'examples/costs/ai-inference-routing/lab.py']),
              ('ai_inference_routing_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/ai-inference-routing','-p','test_*.py','-v']),
              ('live_journey_local_tests',['node','--test','app/live-journey.test.mjs']),
              ('amplify_bundled_lock',[sys.executable,'scripts/check-amplify-bundled-lock.py']),
              ('figure_inventory',[sys.executable,'scripts/check-figure-inventory.py']),
              ('key_use_policy_specimen',[sys.executable,'examples/key-use-policy/check_specimen.py']),
              ('local_guard_tests',[sys.executable,'-m','unittest','discover','-s','scripts/tests','-v'])]
    commands.append(('amplify_note_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/amplify-walkthrough','-p','test_*.py','-v']))
    commands.append(('search_index_ordered',[sys.executable,'examples/search-index/ordered_lab.py']))
    commands.append(('search_index_ordered_tests',[sys.executable,'-m','unittest','discover','-s','examples/search-index','-p','test_ordered_lab.py','-v']))
    commands.append(('protective_control_matrix_tests',[sys.executable,'-m','unittest','discover','-s','examples/protective-control-review','-p','test_*.py','-v']))
    commands.append(('ownership_handoff_tests',[sys.executable,'-m','unittest','discover','-s','examples/ownership-handoff','-p','test_*.py','-v']))
    commands.append(('governed_delivery_tests',[sys.executable,'-m','unittest','discover','-s','examples/governed-delivery','-p','test_*.py','-v']))
    commands.append(('publisher_build_trust',[sys.executable,'examples/frontend-publisher/build-trust-lab.py']))
    commands.append(('publisher_build_trust_tests',[sys.executable,'-m','unittest','discover','-s','examples/frontend-publisher','-p','test_build_trust.py','-v']))
    commands.append(('publisher_policy_source_tests',[sys.executable,'-m','unittest','discover','-s','examples/frontend-publisher','-p','test_policy_source.py','-v']))
    commands.append(('publisher_role_evidence',[sys.executable,'examples/publisher-role-evidence/lab.py']))
    commands.append(('publisher_role_evidence_tests',[sys.executable,'-m','unittest','discover','-s','examples/publisher-role-evidence','-p','test_*.py','-v']))
    commands.append(('dependency_triage',[sys.executable,'examples/dependency-triage/lab.py','examples/dependency-triage/fixture.json']))
    commands.append(('dependency_triage_tests',[sys.executable,'-m','unittest','discover','-s','examples/dependency-triage','-p','test_*.py','-v']))
    commands.append(('notification_evidence',[sys.executable,'examples/notification-evidence/lab.py','examples/notification-evidence/cases.json']))
    commands.append(('notification_evidence_tests',[sys.executable,'-m','unittest','discover','-s','examples/notification-evidence','-p','test_*.py','-v']))
    commands.append(('operational_evidence_join',[sys.executable,'examples/operational-evidence-triage/reconcile.py']))
    commands.append(('operational_evidence_join_tests',[sys.executable,'-m','unittest','discover','-s','examples/operational-evidence-triage','-p','test_*.py','-v']))
    commands.append(('protected_export_local',[sys.executable,'examples/protected-export/local_lab.py']))
    commands.append(('protected_export_persistent',[sys.executable,'examples/protected-export/persistent_lab.py']))
    commands.append(('protected_export_identity_http',[sys.executable,'examples/protected-export/identity_http_lab.py']))
    commands.append(('protected_export_local_tests',[sys.executable,'-m','unittest','discover','-s','examples/protected-export','-p','test_*.py','-v']))
    commands.append(('data_contract_cross_language',[sys.executable,'examples/data-contract/interop_lab.py']))
    commands.append(('data_contract_unicode_policy',[sys.executable,'examples/data-contract/unicode_lab.py']))
    commands.append(('data_contract_unicode_store',[sys.executable,'examples/data-contract/unicode_store_lab.py']))
    commands.append(('data_contract_http_revision',[sys.executable,'examples/data-contract/http_revision_lab.py']))
    commands += [(name,[sys.executable,f'examples/{name}/lab.py']) for name in LABS]
    commands += [('ipam_governance',[sys.executable,'examples/ipam-governance/plan.py']),
                 ('ipam_governance_tests',[sys.executable,'-m','unittest','discover',
                                            '-s','examples/ipam-governance','-p','test_*.py'])]
    commands += [('hybrid_container_placement',[sys.executable,'examples/hybrid-container-placement/review.py']),
                 ('hybrid_container_placement_tests',[sys.executable,'-m','unittest','discover',
                                                       '-s','examples/hybrid-container-placement','-p','test_*.py'])]
    commands.append(('cloudformation_change_review_tests', [sys.executable, '-m', 'unittest', 'discover',
                     '-s', 'examples/cloudformation-change-review', '-p', 'test_*.py']))
    commands.append(('database_attempt_capacity',[sys.executable,'examples/database-capacity/attempts_lab.py']))
    commands.append(('database_attempt_capacity_tests',[sys.executable,'-m','unittest','discover','-s','examples/database-capacity','-p','test_*.py','-v']))
    commands.append(('quota_race_tests',[sys.executable,'-m','unittest','discover','-s','examples/quota-race','-p','test_*.py','-v']))
    commands.append(('relational_capacity_tests',[sys.executable,'-m','unittest','discover','-s','examples/relational-capacity','-p','test_*.py','-v']))
    commands.append(('bulkhead_capacity_tests',[sys.executable,'-m','unittest','discover','-s','examples/bulkhead-capacity','-p','test_*.py','-v']))
    commands.append(('checkpoint_parallel_frontier',[sys.executable,'examples/checkpoint-recovery/parallel_lab.py']))
    commands.append(('container_stop_deadline',[sys.executable,'examples/container-release/deadline_lab.py']))
    commands.append(('dashboard_decision',[sys.executable,'examples/dashboard-grain/decision_lab.py']))
    commands.append(('dashboard_decision_tests',[sys.executable,'-m','unittest','discover','-s','examples/dashboard-grain','-p','test_decision_lab.py','-v']))
    commands.append(('operations_reader_pilot_fixture_tests',[sys.executable,'-m','unittest','discover','-s','examples/learner-pilot','-p','test_operations_case.py','-v']))
    commands += [('schema_overlap_write_gate',[sys.executable,'examples/schema-compatibility/overlap_lab.py']),
                 ('build_inputs',[sys.executable,'examples/local-operations/build_inputs.py']),
                 ('reusable_module_terraform_format',['terraform','fmt','-check','-recursive','examples/reusable-module']),
                 ('artifact_repository_identity',[sys.executable,'examples/artifact-repository-model/publish.py']),
                 ('signed_release_gate',[sys.executable,'-m','unittest','discover','-s','examples/signed-release-gate','-p','test_*.py']),
                 ('artifact_repository_terraform_format',['terraform','fmt','-check','-recursive','examples/artifact-repository-config/terraform']),
                 ('cloudwatch_alert_terraform_format',['terraform','fmt','-check','examples/cloudwatch-alert-path']),
                 ('cloudwatch_alert_agent_json',[sys.executable,'-m','json.tool','examples/cloudwatch-alert-path/agent-config.ec2.json']),
                 ('alarm_diagnostic_pattern_json',[sys.executable,'-m','json.tool','examples/alarm-diagnostic-runbook/event-pattern.json']),
                 ('alarm_diagnostic_event_json',[sys.executable,'-m','json.tool','examples/alarm-diagnostic-runbook/sample-event.json']),
                 ('alarm_diagnostic_runbook_json',[sys.executable,'-m','json.tool','examples/alarm-diagnostic-runbook/diagnostic-runbook.json']),
                 ('alarm_diagnostic_target_input_json',[sys.executable,'-m','json.tool','examples/alarm-diagnostic-runbook/target-input.json']),
                 ('pipeline_testing_negative_controls',[sys.executable,'examples/pipeline-testing/check-negative.py']),
                 ('lost_booking_response',[sys.executable,'examples/network-selection/lost_response.py']),
                 ('global_web_cache_boundary',[sys.executable,'examples/global-web/cache_boundary.py']),
                 ('global_web_failback',[sys.executable,'examples/global-web/failback_lab.py']),
                 ('global_web_conflict',[sys.executable,'examples/global-web/conflict_lab.py']),
                 ('global_web_fence',[sys.executable,'examples/global-web/fence_lab.py']),
                 ('global_web_tests',[sys.executable,'-m','unittest','discover','-s','examples/global-web','-p','test_*.py','-v']),
                 ('media_publication_read_path',[sys.executable,'examples/media-publication/read-path-lab.py']),
                 ('media_publication_cache_boundary',[sys.executable,'examples/media-publication/cache-boundary-lab.py']),
                 ('local_resilience_experiment',[sys.executable,'examples/resilience-exercise/local_lab.py']),
                 ('local_resilience_experiment_tests',[sys.executable,'-m','unittest','discover','-s','examples/resilience-exercise','-p','test_local_lab.py','-v']),
                 ('process_resilience_experiment',[sys.executable,'examples/resilience-exercise/process_lab.py']),
                 ('process_resilience_experiment_tests',[sys.executable,'-m','unittest','discover','-s','examples/resilience-exercise','-p','test_process_lab.py','-v']),
                 ('tenant_recovery',[sys.executable,'examples/recovery-reconciliation/tenant_lab.py']),
                 ('tenant_job_authority',[sys.executable,'examples/tenant-isolation/job_authority_lab.py']),
                 ('tenant_external_effect',[sys.executable,'examples/tenant-isolation/external_effect_lab.py']),
                 ('tenant_job_authority_tests',[sys.executable,'-m','unittest','discover','-s','examples/tenant-isolation','-p','test_*.py','-v']),
                 ('tenant_entitlement_tests',[sys.executable,'-m','unittest','discover','-s','examples/tenant-entitlement','-p','test_*.py','-v']),
                 ('tenant_offboarding_tests',[sys.executable,'-m','unittest','discover','-s','examples/tenant-offboarding','-p','test_*.py','-v']),
                 ('tenant_fairness_tests',[sys.executable,'-m','unittest','discover','-s','examples/tenant-fairness','-p','test_*.py','-v']),
                 ('producer_scope',[sys.executable,'examples/event-reconciliation/producer_lab.py']),
                 ('fleet_reading_ledger',[sys.executable,'examples/fleet-ingress/reading_ledger.py']),
                 ('fleet_failure_journey',[sys.executable,'examples/fleet-ingress/failure_journey.py']),
                 ('fleet_reading_ledger_tests',[sys.executable,'-m','unittest','discover','-s','examples/fleet-ingress','-p','test_*.py','-v']),
                 ('hybrid_path_model',[sys.executable,'examples/hybrid-design/path_lab.py']),
                 ('hybrid_path_model_tests',[sys.executable,'-m','unittest','discover','-s','examples/hybrid-design','-p','test_path_lab.py','-v']),
                 ('hybrid_subnet_path',[sys.executable,'examples/hybrid-design/subnet_path_lab.py']),
                 ('hybrid_subnet_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/hybrid-design','-p','test_subnet_path_lab.py','-v']),
                 ('hybrid_dns_two_directions',[sys.executable,'examples/hybrid-design/dns_path_lab.py']),
                 ('file_intake_two_gate_review',[sys.executable,'examples/file-intake/review_lab.py']),
                 ('file_intake_http_visitor',[sys.executable,'examples/file-intake/visitor_lab.py']),
                 ('file_intake_direct_link_negative_control',[sys.executable,'examples/file-intake/direct_link_lab.py']),
                 ('file_intake_direct_link_tests',[sys.executable,'-m','unittest','discover','-s','examples/file-intake','-p','test_direct_link_lab.py','-v']),
                 ('architecture_transfer_contract_walk',[sys.executable,'examples/architecture-transfer/lab.py']),
                 ('clinic_offline_intake',[sys.executable,'examples/clinic-offline-intake/lab.py']),
                 ('clinic_offline_intake_tests',[sys.executable,'-m','unittest','discover','-s','examples/clinic-offline-intake','-p','test_*.py','-v']),
                 ('food_bank_pickup_journey',[sys.executable,'examples/food-bank-pickup/lab.py']),
                 ('food_bank_pickup_tests',[sys.executable,'-m','unittest','discover','-s','examples/food-bank-pickup','-p','test_lab.py','-v']),
                 ('food_bank_external_stock',[sys.executable,'examples/food-bank-pickup/external_stock.py']),
                 ('food_bank_external_stock_tests',[sys.executable,'-m','unittest','discover','-s','examples/food-bank-pickup','-p','test_external_stock.py','-v']),
                 ('food_bank_stock_http',[sys.executable,'examples/food-bank-pickup/stock_http.py','demo']),
                 ('food_bank_stock_http_tests',[sys.executable,'-m','unittest','discover','-s','examples/food-bank-pickup','-p','test_stock_http.py','-v']),
                 ('architecture_change_impact_tests',[sys.executable,'-m','unittest','discover','-s','examples/architecture-change-impact','-p','test_*.py','-v']),
                 ('well_architected_queue_window',[sys.executable,'examples/well-architected-review/queue_window.py']),
                 ('well_architected_pickup_window',[sys.executable,'examples/well-architected-review/pickup_window.py']),
                 ('well_architected_queue_window_tests',[sys.executable,'-m','unittest','discover','-s','examples/well-architected-review','-p','test_*.py','-v']),
                 ('modernization_outbox',[sys.executable,'examples/modernization-targets/outbox_lab.py']),
                 ('record_revisions',[sys.executable,'examples/data-contract/revision_lab.py']),
                 ('compensation_recovery',[sys.executable,'examples/reservation-holds/compensation_lab.py']),
                 ('a03_schedule_diagnostic',[sys.executable,'examples/reservation-cloud-transition/schedule_diagnostic.py']),
                 ('a03_schedule_diagnostic_tests',[sys.executable,'-m','unittest','discover','-s','examples/reservation-cloud-transition','-p','test_schedule_diagnostic.py','-v']),
                 ('ingestion_deadline',[sys.executable,'examples/ingestion-review/check-model.py']),
                 ('cost_lifecycle',[sys.executable,'examples/costs/lifecycle-exercise.py']),
                 ('a02_contact_cost',[sys.executable,'examples/costs/contact-worklist/lab.py','examples/costs/contact-worklist/scenario.json']),
                 ('a02_contact_receipt_reconciliation',[sys.executable,'examples/costs/contact-worklist/reconcile.py','examples/costs/contact-worklist/synthetic-receipts.json']),
                 ('a02_contact_cost_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/contact-worklist','-p','test_*.py','-v']),
                 ('a02_contact_discovery_choice',[sys.executable,'examples/contact-discovery-choice/lab.py','examples/contact-discovery-choice/case.json']),
                 ('a02_contact_index_cutover',[sys.executable,'examples/contact-discovery-choice/cutover.py','examples/contact-discovery-choice/cutover-case.json']),
                 ('a02_contact_discovery_choice_tests',[sys.executable,'-m','unittest','discover','-s','examples/contact-discovery-choice','-p','test_*.py','-v']),
                 ('amplify_usage_fanout',[sys.executable,'examples/costs/amplify-usage-fanout/lab.py']),
                 ('amplify_usage_fanout_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/amplify-usage-fanout','-p','test_*.py','-v']),
                 ('amplify_selected_public_prices',[sys.executable,'examples/costs/amplify-usage-fanout/public_price_lab.py']),
                 ('ohio_s3_upload_delete',[sys.executable,'examples/storage-cost/ohio-upload-delete/lab.py']),
                 ('ohio_s3_upload_delete_tests',[sys.executable,'-m','unittest','discover','-s','examples/storage-cost/ohio-upload-delete','-p','test_*.py','-v']),
                 ('versioned_s3_read_path',[sys.executable,'examples/storage-cost/versioned-read-path/lab.py']),
                 ('versioned_s3_public_price_path',[sys.executable,'examples/storage-cost/versioned-read-path/priced_lab.py']),
                 ('versioned_s3_read_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/storage-cost/versioned-read-path','-p','test_*.py','-v']),
                 ('cost_reconciliation',[sys.executable,'examples/costs/reconciliation-exercise.py']),
                 ('analytics_rerun_publication',[sys.executable,'examples/analytics-query/rerun_lab.py']),
                 ('analytics_rerun_publication_tests',[sys.executable,'-m','unittest','discover','-s','examples/analytics-query','-p','test_rerun_lab.py','-v']),
                 ('analytics_file_publication',[sys.executable,'examples/analytics-query/file_publication_lab.py']),
                 ('analytics_file_publication_tests',[sys.executable,'-m','unittest','discover','-s','examples/analytics-query','-p','test_file_publication_lab.py','-v']),
                 ('analytics_source_completeness',[sys.executable,'examples/analytics-query/source_completeness_lab.py']),
                 ('analytics_source_completeness_tests',[sys.executable,'-m','unittest','discover','-s','examples/analytics-query','-p','test_source_completeness_lab.py','-v']),
                 ('analytics_competing_publishers',[sys.executable,'examples/analytics-query/competing_publishers_lab.py']),
                 ('analytics_competing_publishers_tests',[sys.executable,'-m','unittest','discover','-s','examples/analytics-query','-p','test_competing_publishers_lab.py','-v']),
              ('cost_optimization_audit',[sys.executable,'examples/costs/optimization-audit/lab.py']),
                 ('cost_optimization_unit_proxy',[sys.executable,'examples/costs/optimization-audit/unit_cost_lab.py']),
                 ('cost_optimization_unit_proxy_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/optimization-audit','-p','test_*.py','-v']),
                 ('resource_intensity',[sys.executable,'examples/costs/resource-intensity.py']),
                 ('demand_alignment',[sys.executable,'examples/demand-alignment/lab.py']),
                 ('demand_alignment_tests',[sys.executable,'-m','unittest','discover','-s','examples/demand-alignment','-p','test_*.py','-v']),
                 ('region_selection',[sys.executable,'examples/region-selection/lab.py']),
                 ('region_selection_tests',[sys.executable,'-m','unittest','discover','-s','examples/region-selection','-p','test_*.py','-v']),
              ('scaling_methods',[sys.executable,'-m','unittest','discover','-s','examples/scaling-methods','-p','test_*.py','-v']),
              ('recovery_automation_gate_tests',[sys.executable,'-m','unittest','discover','-s','examples/recovery-automation','-p','test_*.py','-v']),
              ('recovery_critical_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/recovery-critical-path','-p','test_*.py','-v']),
              ('integrated_restore_tests',[sys.executable,'-m','unittest','discover','-s','examples/integrated-restore','-p','test_lab.py','-v']),
              ('provisioning_receipt_tests',[sys.executable,'-m','unittest','discover','-s','examples/provisioning-receipts','-p','test_*.py','-v']),
              ('pipeline_receipt_tests',[sys.executable,'-m','unittest','discover','-s','examples/pipeline-receipts','-p','test_*.py','-v']),
              ('scaling_policy_model_tests',[sys.executable,'-m','unittest','discover','-s','examples/scaling-policy-model','-p','test_*.py','-v']),
              ('arrival_shape_tests',[sys.executable,'-m','unittest','discover','-s','examples/arrival-shape','-p','test_*.py','-v']),
              ('serverless_db_burst',[sys.executable,'examples/serverless-db-burst/burst_lab.py']),
              ('serverless_db_burst_tests',[sys.executable,'-m','unittest','discover','-s','examples/serverless-db-burst','-p','test_*.py','-v']),
              ('reliability_growth_tests',[sys.executable,'-m','unittest','discover','-s','examples/reliability-growth','-p','test_*.py','-v']),
              ('performance_boundary_review_tests',[sys.executable,'-m','unittest','discover','-s','examples/performance-boundary-review','-p','test_*.py','-v']),
              ('elastic_capacity_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/elastic-capacity-path','-p','test_*.py','-v']),
              ('failover_health_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/failover-health-path','-p','test_*.py','-v']),
              ('regional_customer_path',[sys.executable,'examples/regional-recovery/customer_path_lab.py']),
              ('regional_customer_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/regional-recovery','-p','test_customer_path_lab.py','-v']),
              ('regional_failover_timeline',[sys.executable,'examples/regional-recovery/failover_timeline.py']),
              ('regional_failover_timeline_tests',[sys.executable,'-m','unittest','discover','-s','examples/regional-recovery','-p','test_failover_timeline.py','-v']),
              ('legacy_session_failover',[sys.executable,'examples/legacy-session-failover/legacy_failover.py']),
              ('legacy_session_failover_tests',[sys.executable,'-m','unittest','discover','-s','examples/legacy-session-failover','-p','test_legacy_failover.py','-v']),
              ('a02_contact_operator_claim',[sys.executable,'examples/request-journey/operator_lab.py']),
              ('a02_contact_operator_claim_tests',[sys.executable,'-m','unittest','discover','-s','examples/request-journey','-p','test_operator_lab.py','-v']),
              ('a02_contact_predeadline',[sys.executable,'examples/request-journey/predeadline_lab.py']),
              ('a02_contact_predeadline_tests',[sys.executable,'-m','unittest','discover','-s','examples/request-journey','-p','test_predeadline_lab.py','-v']),
              ('a02_contact_deadline',[sys.executable,'examples/request-journey/deadline_lab.py']),
              ('a02_contact_deadline_tests',[sys.executable,'-m','unittest','discover','-s','examples/request-journey','-p','test_deadline_lab.py','-v']),
              ('monitoring_automation_tests',[sys.executable,'-m','unittest','discover','-s','examples/monitoring-automation','-p','test_*.py','-v']),
              ('ops04_field_lab',[sys.executable,'examples/ops04-field-lab/ledger_lab.py']),
              ('ops04_field_lab_tests',[sys.executable,'-m','unittest','discover','-s','examples/ops04-field-lab','-p','test_*.py','-v']),
              ('alarm_diagnostic_runbook_tests',[sys.executable,'-m','unittest','discover','-s','examples/alarm-diagnostic-runbook','-p','test_*.py','-v']),
              ('operations_closure_tests',[sys.executable,'-m','unittest','discover','-s','examples/operations-closure','-p','test_*.py','-v']),
              ('incident_event_workflow_tests',[sys.executable,'-m','unittest','discover','-s','examples/incident-event-workflow','-p','test_*.py','-v']),
              ('configuration_change_control_tests',[sys.executable,'-m','unittest','discover','-s','examples/configuration-change-control','-p','test_*.py','-v']),
              ('security_audit_evidence_tests',[sys.executable,'-m','unittest','discover','-s','examples/security-audit-evidence','-p','test_*.py','-v']),
              ('agent_tool_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/agent-tool-boundary','-p','test_*.py','-v']),
              ('agent_answer_evaluation_tests',[sys.executable,'-m','unittest','discover','-s','examples/agent-evaluation','-p','test_*.py','-v']),
              ('agent_pre_model_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/agent-evaluation/transfer-school','-p','test_*.py','-v']),
              ('agent_source_to_action_journey',[sys.executable,'examples/agent-tool-boundary/journey.py']),
              ('policy_precedence',[sys.executable,'examples/policy-precedence/lab.py']),
              ('policy_precedence_tests',[sys.executable,'-m','unittest','discover','-s','examples/policy-precedence','-p','test_*.py','-v']),
              ('three_tier_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/three-tier-boundary','-p','test_*.py','-v']),
              ('platform_transfer_whole_run',[sys.executable,'examples/platform-transfer/whole_run_lab.py']),
              ('platform_transfer_whole_run_tests',[sys.executable,'-m','unittest','discover','-s','examples/platform-transfer','-p','test_*.py','-v']),
              ('service_entry_bypass',[sys.executable,'examples/service-communication/proxy_bypass_lab.py']),
              ('service_entry_replay',[sys.executable,'examples/service-communication/replay_boundary_lab.py']),
              ('service_entry_replay_tests',[sys.executable,'-m','unittest','discover','-s','examples/service-communication','-p','test_replay_boundary_lab.py','-v']),
              ('service_process_replay',[sys.executable,'examples/service-communication/process_replay_lab.py']),
              ('service_process_replay_tests',[sys.executable,'-m','unittest','discover','-s','examples/service-communication','-p','test_process_replay_lab.py','-v']),
              ('modernization_outbox_tests',[sys.executable,'-m','unittest','discover','-s','examples/modernization-targets','-p','test_*.py','-v']),
                 ('api_compatibility',[sys.executable,'examples/api-contract/compatibility_lab.py']),
                 ('two_reviewer_admission',[sys.executable,'examples/approval-workflow/two_reviewer_lab.py']),
                 ('approval_external_effect',[sys.executable,'examples/approval-workflow/external_effect_lab.py']),
                 ('approval_external_effect_tests',[sys.executable,'-m','unittest','discover','-s','examples/approval-workflow','-p','test_external_effect_lab.py','-v']),
                 ('approval_external_cancel',[sys.executable,'examples/approval-workflow/external_cancel_lab.py']),
                 ('approval_external_cancel_tests',[sys.executable,'-m','unittest','discover','-s','examples/approval-workflow','-p','test_external_cancel_lab.py','-v']),
                 ('approval_visitor_path',[sys.executable,'examples/approval-workflow/visitor_path.py']),
                 ('approval_visitor_path_tests',[sys.executable,'-m','unittest','discover','-s','examples/approval-workflow','-p','test_visitor_path.py','-v']),
                 ('environment_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/environment-boundary','-p','test_*.py','-v']),
                 ('migration_cutover_visitor',[sys.executable,'examples/migration-cutover/visitor.py']),
                 ('mainframe_normalized_comparison',[sys.executable,'examples/mainframe-modernization/reconcile.py','examples/mainframe-modernization/source.csv','examples/mainframe-modernization/candidate.csv']),
                 ('mainframe_normalized_comparison_tests',[sys.executable,'-m','unittest','discover','-s','examples/mainframe-modernization','-p','test_*.py','-v']),
                 ('cross_account_archive_audit',[sys.executable,'examples/cross-account-log-archive/audit.py','examples/cross-account-log-archive/source.jsonl','examples/cross-account-log-archive/archive.jsonl']),
                 ('cross_account_archive_audit_tests',[sys.executable,'-m','unittest','discover','-s','examples/cross-account-log-archive','-p','test_*.py','-v']),
                 ('migration_reverse_replay',[sys.executable,'examples/migration-cutover/reverse_lab.py']),
                 ('migration_reverse_replay_tests',[sys.executable,'-m','unittest','discover','-s','examples/migration-cutover','-p','test_reverse_lab.py','-v']),
                 ('migration_outside_effect_return',[sys.executable,'examples/migration-cutover/effect_return_lab.py']),
                 ('migration_outside_effect_return_tests',[sys.executable,'-m','unittest','discover','-s','examples/migration-cutover','-p','test_effect_return_lab.py','-v']),
                 ('migration_versioned_return',[sys.executable,'examples/migration-cutover/versioned_return_lab.py']),
                 ('migration_versioned_return_tests',[sys.executable,'-m','unittest','discover','-s','examples/migration-cutover','-p','test_versioned_return_lab.py','-v']),
                 ('migration_cutover_write_gap',[sys.executable,'examples/migration-cutover/write_gap.py']),
                 ('migration_db_epoch',[sys.executable,'examples/migration-cutover/db_epoch_lab.py']),
                 ('migration_db_epoch_tests',[sys.executable,'-m','unittest','discover','-s','examples/migration-cutover','-p','test_db_epoch_lab.py','-v']),
                 ('credit_commitments',[sys.executable,'examples/costs/credit-commitments/lab.py']),
                 ('credit_commitments_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/credit-commitments','-p','test_*.py','-v']),
                 ('retry_budget',[sys.executable,'examples/retry-budget/lab.py']),
                 ('retry_budget_tests',[sys.executable,'-m','unittest','discover','-s','examples/retry-budget','-p','test_*.py','-v']),
                 ('reader_budget_decision',[sys.executable,'examples/costs/reader-budget-decision/lab.py']),
                 ('reader_budget_decision_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/reader-budget-decision','-p','test_*.py','-v']),
                 ('pricing_commitment',[sys.executable,'examples/costs/pricing-commitment/compare.py']),
                 ('pricing_commitment_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/pricing-commitment','-p','test_*.py','-v']),
                 ('credit_decision',[sys.executable,'examples/credit-decision/lab.py']),
                 ('credit_decision_tests',[sys.executable,'-m','unittest','discover','-s','examples/credit-decision','-p','test_*.py','-v']),
                 ('self_managed_hosting_cost',[sys.executable,'examples/costs/self-managed-hosting/assess.py','examples/costs/self-managed-hosting/plan.json']),
                 ('self_managed_hosting_cost_tests',[sys.executable,'-m','unittest','discover','-s','examples/costs/self-managed-hosting','-p','test_*.py','-v']),
                 ('oidc_trust_boundary',[sys.executable,'examples/oidc-trust-boundary/lab.py']),
                 ('oidc_trust_boundary_tests',[sys.executable,'-m','unittest','discover','-s','examples/oidc-trust-boundary','-p','test_*.py','-v']),
                 ('retry',['node','examples/advanced/retry-lab.mjs']),
                 ('capstone_fixture',[sys.executable,'examples/capstones/check-evidence.py']),
                 ('capstone_cohort',[sys.executable,'examples/capstones/cohort_lab.py']),
                 ('capstone_cohort_tests',[sys.executable,'-m','unittest','discover','-s','examples/capstones','-p','test_cohort_lab.py','-v']),
                 ('capstone_intake_completeness',[sys.executable,'examples/capstones/intake_completeness_lab.py']),
                 ('capstone_intake_completeness_tests',[sys.executable,'-m','unittest','discover','-s','examples/capstones','-p','test_intake_completeness_lab.py','-v'])]
    if args.app_toolchain:
        commands.append(('app_dependency_compatibility',['node','examples/dependency-compatibility/check.cjs','app']))
        commands.append(('app_output_validation',['node','examples/dependency-compatibility/check-output-validation.cjs','app']))
        commands.append(('app_mysql_configuration',['node','examples/dependency-compatibility/check-mysql-config.cjs','app']))
        commands.append(('amplify_secret_boundary',[sys.executable,'examples/amplify-secret-boundary/lab.py']))
        commands.append(('amplify_secret_server_boundary',[sys.executable,'examples/amplify-secret-boundary/server_lab.py']))
        commands.append(('app_build',['npm','run','build','--prefix','app']))
    else:
        report['checks'].append({'name':'amplify_secret_boundary','status':'not_requested','reason':'Supply --app-toolchain with locked app dependencies installed'})
        commands.append(('amplify_secret_server_boundary',[sys.executable,'examples/amplify-secret-boundary/server_lab.py']))
        for name in ['app_mysql_configuration']:
            report['checks'].append({'name':name,'status':'not_requested','reason':'Supply --app-toolchain with locked app dependencies installed'})
        report['checks'].append({'name':'app_dependency_compatibility','status':'not_requested','reason':'Supply --app-toolchain with locked app dependencies installed'})
        report['checks'].append({'name':'app_build','status':'not_requested','reason':'Supply --app-toolchain with app dependencies and local client configuration available'})
    if args.frontend_publisher_toolchain:
        commands.append(('frontend_config_build_boundary',[sys.executable,'examples/frontend-publisher/config-build-lab.py']))
    else:
        report['checks'].append({'name':'frontend_config_build_boundary','status':'not_requested','reason':'Supply --frontend-publisher-toolchain with locked frontend publisher dependencies installed'})
    if args.analytics_python:
        commands.append(('analytics_query',[str(args.analytics_python.absolute()),'examples/analytics-query/lab.py']))
        commands.append(('analytics_schema',[str(args.analytics_python.absolute()),'examples/analytics-query/schema_lab.py']))
        commands.append(('analytics_evolution',[str(args.analytics_python.absolute()),'examples/analytics-query/evolution_lab.py']))
    else:
        report['checks'].append({'name':'analytics_query','status':'not_requested','reason':'Supply --analytics-python with pinned DuckDB'})
        report['checks'].append({'name':'analytics_schema','status':'not_requested','reason':'Supply --analytics-python with pinned DuckDB'})
        report['checks'].append({'name':'analytics_evolution','status':'not_requested','reason':'Supply --analytics-python with pinned DuckDB'})
    if args.containers:
        commands.append(('container_release',[sys.executable,'examples/container-release/lab.py']))
        commands.append(('container_shutdown_negative',[sys.executable,'examples/container-release/check-negative.py']))
        commands.append(('container_business_negative',[sys.executable,'examples/container-release/check-business-negative.py']))
    else:
        report['checks'].append({'name':'container_release','status':'not_requested','reason':'Supply --containers with a running Docker engine'})
        report['checks'].append({'name':'container_shutdown_negative','status':'not_requested','reason':'Supply --containers with a running Docker engine'})
        report['checks'].append({'name':'container_business_negative','status':'not_requested','reason':'Supply --containers with a running Docker engine'})
    if args.domain_python:
        commands.append(('emulated_architectures',[str(args.domain_python.absolute()),'-m','unittest','discover','-s','architectures/reliable-workflows/tests','-v']))
        commands.append(('a02_customer_request_journey',[str(args.domain_python.absolute()),'examples/request-journey/lab.py']))
        commands.append(('integrated_restore_s3_moto',[str(args.domain_python.absolute()),'examples/integrated-restore/s3_version_lab.py']))
        commands.append(('integrated_restore_s3_moto_tests',[str(args.domain_python.absolute()),'-m','unittest','discover','-s','examples/integrated-restore','-p','test_s3_version_lab.py','-v']))
        commands.append(('versioned_restore_cost_bridge',[str(args.domain_python.absolute()),'examples/storage-cost/versioned-read-path/emulated_restore_bridge.py']))
        commands.append(('versioned_restore_cost_bridge_tests',[str(args.domain_python.absolute()),'-m','unittest','discover','-s','examples/storage-cost/versioned-read-path','-p','moto_restore_bridge_tests.py','-v']))
    else:
        report['checks'].append({'name':'a02_customer_request_journey','status':'not_requested','reason':'Supply --domain-python with pinned Moto'})
        report['checks'].append({'name':'emulated_architectures','status':'not_requested','reason':'Supply --domain-python; this is not a passing result'})
        report['checks'].append({'name':'integrated_restore_s3_moto','status':'not_requested','reason':'Supply --domain-python with pinned boto3 and Moto'})
        report['checks'].append({'name':'integrated_restore_s3_moto_tests','status':'not_requested','reason':'Supply --domain-python with pinned boto3 and Moto'})
        report['checks'].append({'name':'versioned_restore_cost_bridge','status':'not_requested','reason':'Supply --domain-python with pinned boto3 and Moto'})
        report['checks'].append({'name':'versioned_restore_cost_bridge_tests','status':'not_requested','reason':'Supply --domain-python with pinned boto3 and Moto'})
    with tempfile.TemporaryDirectory(prefix='amplify-check-config-') as temporary:
        empty=Path(temporary)/'empty';empty.write_text('')
        env={k:v for k,v in os.environ.items() if not k.startswith(('AWS_','TF_')) and k!='PYTHONOPTIMIZE'}
        env.update(AWS_CONFIG_FILE=str(empty),AWS_SHARED_CREDENTIALS_FILE=str(empty),AWS_EC2_METADATA_DISABLED='true',
                   AWS_ACCESS_KEY_ID='testing',AWS_SECRET_ACCESS_KEY='testing',AWS_DEFAULT_REGION='us-east-2')
        for name,command in commands:
            try:
                result=subprocess.run(command,cwd=BASE,env=env,text=True,capture_output=True,timeout=120)
                item={'name':name,'status':'passed' if result.returncode==0 else 'failed','exit_code':result.returncode,
                      'stdout':result.stdout,'stderr':result.stderr}
            except (OSError,subprocess.TimeoutExpired) as error:
                item={'name':name,'status':'failed','error':str(error)}
            report['checks'].append(item);print(name+': '+item['status'],flush=True)
    broken=[];local_only=[];checked=0
    for directory in ['book','curriculum','docs','examples','.']:
        paths = [BASE/'README.md'] if directory == '.' else (BASE/directory).rglob('*.md')
        for path in paths:
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' in link or link.startswith(('#','mailto:')):continue
                target=unquote(link.split('#')[0]);checked+=1
                resolved=(path.parent/target).resolve()
                if not resolved.exists():
                    item={'file':str(path.relative_to(BASE)),'target':link}
                    (local_only if documented_local_only(BASE,path,resolved) else broken).append(item)
    report['checks'].append({'name':'local_document_paths','status':'failed' if broken else 'passed','checked':checked,'broken':broken,
                              'local_only':local_only,
                              'scope':'Markdown target paths only; known local-only Word/workspace references reported separately; anchors and external URLs are not verified'})
    changed=[name for name,digest in sources.items() if not (BASE/name).is_file()
             or hashlib.sha256((BASE/name).read_bytes()).hexdigest()!=digest]
    report['checks'].append({'name':'source_unchanged','status':'failed' if changed else 'passed','changed':changed})
    report['source_basis']=source_basis
    report['source_sha256']=sources
    report['all_requested_passed']=all(c['status']!='failed' for c in report['checks'])
    destination=BASE/'artifacts/companion-checks.json';destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(f'Report: {destination}')
    if broken:print(json.dumps(broken,indent=2))
    return 0 if report['all_requested_passed'] else 1

if __name__=='__main__':raise SystemExit(main())

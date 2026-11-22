'use strict';
document.querySelectorAll('form[data-model]').forEach(form => {
  const output = form.querySelector('.result');
  form.addEventListener('input', () => { output.hidden = true; output.replaceChildren(); });
  const run = event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const values = new FormData(form);
    const kind = form.dataset.model;
    let result, title;
    if (kind === 'request') {
      result = AwsLearningModels.request({ allowed: values.get('allowed') === 'yes', failure: values.get('failure') });
      title = `${result.saved ? 'One repair saved' : 'No repair saved'}; ${result.known ? 'the customer receives a result' : 'the customer has no confirmation'}.`;
    } else if (kind === 'retry') {
      result = AwsLearningModels.retry(Object.fromEntries(['firstSaved', 'retry', 'sameKey', 'deduplicate'].map(key => [key, values.has(key)])));
      title = `${result.records} repair record${result.records === 1 ? '' : 's'} in this model.`;
    } else {
      result = AwsLearningModels.recovery(Object.fromEntries(['interval', 'restore', 'lossTarget', 'timeTarget'].map(key => [key, Number(values.get(key))])));
      title = `Data-loss target: ${result.lossFits ? 'fits' : 'missed'}. Recovery-time target: ${result.timeFits ? 'fits' : 'missed'}.`;
    }
    const heading = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = title; heading.append(strong);
    output.replaceChildren(heading);
    if (result.steps) {
      const sequence = document.createElement('ol');
      result.steps.forEach(step => { const item = document.createElement('li'); item.textContent = step; sequence.append(item); });
      output.append(sequence);
    }
    const explanation = document.createElement('p'); explanation.textContent = result.lesson;
    output.append(explanation); output.hidden = false;
  };
  form.addEventListener('submit', run);
  const button = form.querySelector('button');
  button.addEventListener('click', run);
  if (typeof AwsLearningModels !== 'undefined') button.disabled = false;
});

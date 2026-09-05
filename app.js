document.documentElement.classList.add('js');

const essayDesigns = {
  1: {steps: [['LLM', 'Write essay']], explanation: 'One call produces the finished essay. There is no separate research or revision step. This is the baseline to compare with the longer workflows.'},
  3: {steps: [['LLM', 'Outline'], ['TOOL', 'Research'], ['LLM', 'Draft']], explanation: 'The outline guides research, and the retrieved material informs the draft. This adds evidence, but there is still no separate check of the finished draft.'},
  5: {steps: [['LLM', 'Outline'], ['TOOL', 'Research'], ['LLM', 'Draft'], ['LLM', 'Review'], ['LLM', 'Revise']], explanation: 'The five-step version creates a first draft, reviews it, and uses that feedback to revise. Each output becomes an input to later work.'}
};
document.querySelectorAll('[data-essay]').forEach(button => button.addEventListener('click', () => {
  const design = essayDesigns[button.dataset.essay];
  document.querySelectorAll('[data-essay]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  const flow = document.querySelector('#essay-flow');
  flow.replaceChildren(...design.steps.map(([owner, title], index) => {
    const li = document.createElement('li');
    if (owner === 'TOOL') li.classList.add('tool');
    const label = document.createElement('small');
    label.textContent = `${String(index + 1).padStart(2, '0')} · ${owner}`;
    const name = document.createElement('b'); name.textContent = title;
    li.append(label, name); return li;
  }));
  document.querySelector('#essay-explanation').textContent = design.explanation;
}));

const traceSteps = [
  {title: 'Extract the request', description: 'A model step identifies the fields needed by the rest of the workflow.', input: 'Susan’s email about order #8847', output: 'order_id: "8847"\nexpected: "blue blender"\nreceived: "red toaster"\ndeadline: "this weekend"', effect: 'none'},
  {title: 'Look up the order', description: 'Application code queries the fixture using the extracted order ID.', input: 'order_id: "8847"', output: 'product: "blue blender"\nstatus: "delivered"', effect: 'read-only lookup'},
  {title: 'Draft the reply', description: 'The draft uses both the customer’s request and the retrieved record.', input: 'request: extracted fields\norder: verified record', output: '“I’m sorry you received a red toaster instead of your blue blender. I understand you need it this weekend. Our team will review the delivery issue.”', effect: 'none'},
  {title: 'Review the draft', description: 'A fixture supplies the review decision; the application uses it to decide whether to continue.', input: 'draft', output: 'approved: true', effect: 'review recorded'},
  {title: 'Simulate sending', description: 'Only the approved route appends the draft to the local outbox.', input: 'approved draft', output: 'receipt: "SIMULATED-001"\noutbox: 0 → 1 message', effect: 'one simulated outbox write'}
];
let currentStep = 0;
const outcome = document.querySelector('#review-outcome');
function renderTrace() {
  const rejected = outcome.value === 'rejected';
  const count = rejected ? 4 : 5;
  currentStep = Math.min(currentStep, count - 1);
  const step = traceSteps[currentStep];
  document.querySelector('#trace-title').textContent = `${currentStep + 1}. ${step.title}`;
  document.querySelector('#trace-description').textContent = rejected && currentStep === 3 ? 'Review is rejected. The application stops here; the send step is never invoked.' : step.description;
  document.querySelector('#trace-input').textContent = step.input;
  document.querySelector('#trace-output').textContent = rejected && currentStep === 3 ? 'approved: false\nstatus: "review_rejected"\noutbox: 0 messages' : step.output;
  document.querySelector('#trace-effect').textContent = `State effect: ${step.effect} · ${currentStep + 1} of ${count} steps`;
  document.querySelectorAll('[data-step]').forEach(button => {
    button.disabled = rejected && Number(button.dataset.step) === 4;
    button.setAttribute('aria-pressed', String(Number(button.dataset.step) === currentStep));
  });
  document.querySelector('#next-step').textContent = currentStep === count - 1 ? 'Start again ↺' : 'Next step →';
}
document.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => {currentStep = Number(button.dataset.step); renderTrace();}));
outcome?.addEventListener('change', () => {currentStep = 3; renderTrace();});
document.querySelector('#next-step')?.addEventListener('click', () => {currentStep = (currentStep + 1) % (outcome.value === 'rejected' ? 4 : 5); renderTrace();});

document.querySelectorAll('.copy').forEach(button => button.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText((button.dataset.copy ? document.getElementById(button.dataset.copy) : button.closest('.code-panel').querySelector('code')).textContent);
    button.textContent = 'Copied';
  } catch {button.textContent = 'Select code to copy';}
  setTimeout(() => {button.textContent = 'Copy';}, 2200);
}));

const checks = [...document.querySelectorAll('[data-mastery]')];
const storageKey = `agentic-notebook-module${document.body.dataset.module || '1'}-mastery-v1`;
let storageAvailable = true;
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
  checks.forEach(box => {box.checked = saved[box.dataset.mastery] === true;});
} catch {storageAvailable = false;}
function updateMastery(save = false) {
  if (save) {
    try {localStorage.setItem(storageKey, JSON.stringify(Object.fromEntries(checks.map(box => [box.dataset.mastery, box.checked]))));}
    catch {storageAvailable = false;}
  }
  const completed = checks.filter(box => box.checked).length;
  if (document.querySelector('#mastery-status')) document.querySelector('#mastery-status').textContent = `${completed} of 4 checked · ${storageAvailable ? 'Saved in this browser.' : 'Available for this visit; browser storage is unavailable.'}`;
}
checks.forEach(box => box.addEventListener('change', () => updateMastery(true)));
updateMastery();

const sections = [...document.querySelectorAll('.lesson')];
const links = [...document.querySelectorAll('.toc a')];
let scheduled = false;
function updateReading() {
  const offset = innerWidth <= 760 ? 145 : 140;
  let active = sections[0];
  for (const section of sections) if (section.getBoundingClientRect().top <= offset) active = section;
  links.forEach(link => {
    if (active && link.hash === `#${active.id}`) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  });
  const max = document.documentElement.scrollHeight - innerHeight;
  document.querySelector('.reading-progress').style.width = `${max > 0 ? Math.min(100, Math.max(0, scrollY / max * 100)) : 0}%`;
  scheduled = false;
}
addEventListener('scroll', () => {if (!scheduled) {scheduled = true; requestAnimationFrame(updateReading);}}, {passive: true});
addEventListener('resize', updateReading);
document.querySelectorAll('.mobile-toc a').forEach(link => link.addEventListener('click', () => {document.querySelector('.mobile-toc').open = false;}));
updateReading();

// The course library reflects only checklists saved on this browser.
document.querySelectorAll('[data-course-progress]').forEach(label => {
  try {
    const saved = JSON.parse(localStorage.getItem(`agentic-notebook-module${label.dataset.courseProgress}-mastery-v1`) || '{}');
    const count = Math.min(4, Object.values(saved).filter(value => value === true).length);
    label.textContent = count ? `${count}/4 learning checks completed` : '4 learning checks';
  } catch { label.textContent = '4 learning checks'; }
});

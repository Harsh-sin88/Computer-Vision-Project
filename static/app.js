async function loadSummary() {
  const res = await fetch('/attendance/today');
  const data = await res.json();
  document.getElementById('summary').innerHTML = `
    <p>${data.date} — ${data.present_count}/${data.total_students} present (${data.attendance_percentage}%)</p>
    <ul>${data.present.map(p => `<li>${p.name} (${p.roll_number}) at ${p.time}</li>`).join('')}</ul>
  `;
}

async function createStudent() {
  const name = document.getElementById('name').value;
  const roll = document.getElementById('roll').value;
  const body = new FormData();
  body.append('name', name);
  body.append('roll_number', roll);
  const res = await fetch('/students', { method: 'POST', body });
  const data = await res.json();
  document.getElementById('enrollMsg').innerText = res.ok
    ? `Registered ${data.name} as label_id ${data.label_id}. Use this label ID below.`
    : `Error: ${JSON.stringify(data)}`;
}

async function uploadSample() {
  const labelId = document.getElementById('labelId').value;
  const file = document.getElementById('sampleFile').files[0];
  const body = new FormData();
  body.append('file', file);
  const res = await fetch(`/students/${labelId}/samples`, { method: 'POST', body });
  const data = await res.json();
  document.getElementById('sampleMsg').innerText = res.ok
    ? `Sample saved: ${data.path}`
    : `Error: ${JSON.stringify(data)}`;
}

async function trainModel() {
  const res = await fetch('/model/train', { method: 'POST' });
  const data = await res.json();
  document.getElementById('trainMsg').innerText = res.ok
    ? `Trained on ${data.students_trained} students, ${data.total_samples} samples`
    : `Error: ${JSON.stringify(data)}`;
}

async function recognize() {
  const file = document.getElementById('recognizeFile').files[0];
  const body = new FormData();
  body.append('file', file);
  const res = await fetch('/attendance/recognize', { method: 'POST', body });
  const data = await res.json();
  document.getElementById('recognizeMsg').innerText = JSON.stringify(data, null, 2);
  loadSummary();
}

loadSummary();

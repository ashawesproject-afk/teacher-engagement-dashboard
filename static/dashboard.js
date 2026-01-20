let chart;

function initChart() {
  const ctx = document.getElementById("chart");
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{ label: "Engagement", data: [], tension: 0.4 }]
    },
    options: { scales: { y: { min: 0, max: 1 } } }
  });
}

function alertText(e) {
  if (e < 0.4) return "⚠ Low engagement";
  if (e < 0.6) return "Medium engagement";
  return "✅ Good engagement";
}

function setText(id, v) {
  document.getElementById(id).textContent = v;
}

function renderStudents(students) {
  const tbody = document.getElementById("studentsBody");
  if (!students || students.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-muted">No student data yet</td></tr>`;
    return;
  }

  // sort by lowest attention first (so teacher notices)
  const sorted = [...students].sort((a, b) => (a.attention ?? 0) - (b.attention ?? 0));

  tbody.innerHTML = sorted.map(s => `
    <tr>
      <td>${s.id}</td>
      <td>${s.activity}</td>
      <td>${s.engaged ? "Yes" : "No"}</td>
      <td>${s.attention}</td>
      <td>${s.last_seen}</td>
    </tr>
  `).join("");
}

async function refresh() {
  const teacherId = document.getElementById("teacherSelect").value;
  const res = await fetch(`/api/latest?teacher_id=${encodeURIComponent(teacherId)}`);
  const data = await res.json();

  const e = data.engagement || 0;

  setText("time", "Last update: " + (data.timestamp || "--"));
  setText("engagement", Math.round(e * 100) + "%");
  setText("total", data.total || 0);

  const c = data.counts || {};
  setText("reading", c.reading || 0);
  setText("writing", c.writing || 0);
  setText("hand_raise", c.hand_raise || 0);
  setText("phone", c.phone || 0);
  setText("other", c.other || 0);

  setText("alert", alertText(e));

  const history = data.history || [];
  chart.data.labels = history.map(x => x.t);
  chart.data.datasets[0].data = history.map(x => x.e);
  chart.update();

  renderStudents(data.students || []);
}

window.onload = () => {
  initChart();
  refresh();
  setInterval(refresh, 2000);

  document.getElementById("teacherSelect").addEventListener("change", () => {
    refresh();
  });
};

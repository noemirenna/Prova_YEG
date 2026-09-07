const API_BASE_URL = "http://localhost:8000";
const charts = { funnel: null, stakeholders: null, daily: null };

const chartColors = ["#237c7a", "#e08b3e", "#d95757", "#4d6fa9", "#8b6bb1"];

function endpoint(path, region) {
	const url = new URL(`${API_BASE_URL}${path}`);
	if (region) url.searchParams.set("region", region);
	return url;
}

async function request(path, region) {
	const response = await fetch(endpoint(path, region));
	if (!response.ok) throw new Error(`HTTP ${response.status}`);
	return response.json();
}

function setStatus(name, message, type = "") {
	const status = document.getElementById(`${name}-status`);
	status.textContent = message;
	status.className = `chart-status ${type}`.trim();
}

function clearChart(name) {
	if (charts[name]) charts[name].destroy();
	charts[name] = null;
}

function createChart(name, canvasId, config) {
	clearChart(name);
	charts[name] = new Chart(document.getElementById(canvasId), config);
}

async function loadRegions() {
	const filter = document.getElementById("region-filter");
	try {
		const data = await request("/participants?limit=100");
		const regions = [...new Set(data.participants.map((item) => item.region).filter(Boolean))].sort();
		regions.forEach((region) => {
			const option = document.createElement("option");
			option.value = region;
			option.textContent = region;
			filter.appendChild(option);
		});
	} catch (error) {
		filter.disabled = true;
	}
}

async function loadFunnel(region) {
	setStatus("funnel", "Caricamento dati...");
	try {
		const data = await request("/dashboard/funnel", region);
		const values = [data.reached, data.stand, data.reserved_room, data.symposium];
		if (values.every((value) => value === 0)) {
			clearChart("funnel");
			setStatus("funnel", "Nessun dato disponibile", "is-empty");
			return;
		}
		createChart("funnel", "funnel-chart", {
			type: "bar",
			data: { labels: ["Raggiunti", "Stand", "Sala VIP", "Simposio"], datasets: [{ data: values, backgroundColor: chartColors }] },
			options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
		});
		setStatus("funnel", "");
	} catch (error) {
		clearChart("funnel");
		setStatus("funnel", "Errore nel caricamento dei dati", "is-error");
	}
}

async function loadStakeholders(region) {
	setStatus("stakeholders", "Caricamento dati...");
	try {
		const data = await request("/dashboard/stakeholders", region);
		if (!data.length) {
			clearChart("stakeholders");
			setStatus("stakeholders", "Nessun dato disponibile", "is-empty");
			return;
		}
		createChart("stakeholders", "stakeholders-chart", {
			type: "doughnut",
			data: { labels: data.map((item) => item.stakeholder), datasets: [{ data: data.map((item) => item.count), backgroundColor: chartColors }] },
			options: { responsive: true, maintainAspectRatio: false }
		});
		setStatus("stakeholders", "");
	} catch (error) {
		clearChart("stakeholders");
		setStatus("stakeholders", "Errore nel caricamento dei dati", "is-error");
	}
}

async function loadDaily(region) {
	setStatus("daily", "Caricamento dati...");
	try {
		const data = await request("/dashboard/daily", region);
		if (!data.length) {
			clearChart("daily");
			setStatus("daily", "Nessun dato disponibile", "is-empty");
			return;
		}
		createChart("daily", "daily-chart", {
			type: "line",
			data: { labels: data.map((item) => item.day), datasets: [{ label: "Partecipanti", data: data.map((item) => item.count), borderColor: "#237c7a", backgroundColor: "rgba(35, 124, 122, 0.12)", fill: true, tension: 0.25 }] },
			options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
		});
		setStatus("daily", "");
	} catch (error) {
		clearChart("daily");
		setStatus("daily", "Errore nel caricamento dei dati", "is-error");
	}
}

async function loadDashboard() {
	const region = document.getElementById("region-filter").value;
	await Promise.all([loadFunnel(region), loadStakeholders(region), loadDaily(region)]);
}

document.getElementById("region-filter").addEventListener("change", loadDashboard);
loadRegions();
loadDashboard();

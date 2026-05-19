const CSV_URL =
"https://docs.google.com/spreadsheets/d/e/2PACX-1vSRPBjaqdSQsWOaN35oSpdQN0c5yoy3ulgDgYJG96Rm4WMgHLyfz_LSOysBECDtjg/pub?gid=577921792&single=true&output=csv";

async function cargarDatos() {
  try {
    const response = await fetch(CSV_URL + "&cache=" + Date.now());
    const text = await response.text();

    const filas = text.split("\n");

    const universidadesPermitidas = [
      "Universidad Central del Ecuador",
      "Universidad Politécnica Salesiana",
      "Pontificia Universidad Católica",
      "Universidad Técnica Particular de Loja",
      "Universidad Técnica de Cotopaxi",
      "Universidad Técnica de Manabí",
      "Universidad de Especialidades Espíritu Santo",
      "Universidad Estatal de Bolívar"
    ];

    let data = [];

    filas.forEach(fila => {
      const c = fila.split(",");
      const universidad = c[0]?.trim();

      if (universidadesPermitidas.includes(universidad)) {
        data.push({
          universidad,
          asignados: numero(c[1]),
          subidos: numero(c[2]),
          aprobados: numero(c[3]),
          devueltos: numero(c[4]),
          falso: numero(c[5]),
          enganoso: numero(c[6]),
          verdadero: numero(c[7]),
          satira: numero(c[8]),
          inverificable: numero(c[9])
        });
      }
    });

    pintar(data);

  } catch (error) {
    console.error("Error cargando datos:", error);
  }
}

function numero(valor) {
  const n = parseInt(valor);
  return isNaN(n) ? 0 : n;
}

function pintar(data) {
  let subidos = 0;
  let aprobados = 0;
  let pendientes = 0;
  let falsos = 0;
  let enganosos = 0;
  let verdaderos = 0;
  let satiras = 0;
  let inverificables = 0;

  data.forEach(u => {
    subidos += u.subidos;
    aprobados += u.aprobados;
    pendientes += Math.max(u.asignados - u.aprobados, 0);

    falsos += u.falso;
    enganosos += u.enganoso;
    verdaderos += u.verdadero;
    satiras += u.satira;
    inverificables += u.inverificable;
  });

  document.getElementById("subidos").innerText = subidos;
  document.getElementById("aprobados").innerText = aprobados;
  document.getElementById("pendientes").innerText = pendientes;
  document.getElementById("universidades").innerText = data.length;

  document.getElementById("falsos").innerText = falsos;
  document.getElementById("enganosos").innerText = enganosos;
  document.getElementById("verdaderos").innerText = verdaderos;
  document.getElementById("satiras").innerText = satiras;
  document.getElementById("inverificables").innerText = inverificables;

  const cards = document.getElementById("cards");
  cards.innerHTML = "";

  data.forEach(u => {
    cards.innerHTML += `
      <div class="card">
        <h2>${u.universidad}</h2>

        <hr>

        <p>🔴 Falso: <strong>${u.falso}</strong></p>
        <p>🟠 Engañoso: <strong>${u.enganoso}</strong></p>
        <p>🟢 Verdadero: <strong>${u.verdadero}</strong></p>
        <p>🟣 Sátira: <strong>${u.satira}</strong></p>
        <p>⚫ Inverificable: <strong>${u.inverificable}</strong></p>
      </div>
    `;
  });
}

cargarDatos();

setInterval(cargarDatos, 5000);
async function showQuran() {
  const res = await fetch("https://api.alquran.cloud/v1/surah");
  const data = await res.json();

  const surahs = data.data;
  const container = document.getElementById("content");
  container.innerHTML = "<h2>بەشی سۆرەکان هەڵبژێرە</h2>";
  container.className = "grid container";

  surahs.forEach(s => {
    const btn = document.createElement("button");
    btn.textContent = `${s.number}: ${s.name}`;
    btn.className = "button";
    btn.onclick = () => showAyahs(s.number, s.name, s.numberOfAyahs);
    container.appendChild(btn);
  });
}

async function showAyahs(surah, name, count) {
  const container = document.getElementById("content");
  container.innerHTML = `<h2>سۆرەی ${name} - ژمارەی ئایەت هەڵبژێرە</h2>`;
  container.className = "grid container";

  for (let i = 1; i <= count; i++) {
    const btn = document.createElement("button");
    btn.textContent = `ئایەت ${i}`;
    btn.className = "button";
    btn.onclick = () => fetchAyah(surah, i);
    container.appendChild(btn);
  }
}

async function fetchAyah(surah, ayah) {
  const arabicRes = await fetch(`https://api.alquran.cloud/v1/ayah/${surah}:${ayah}/ar`);
  const kurdishRes = await fetch(`https://api.alquran.cloud/v1/ayah/${surah}:${ayah}/ku.asan`);

  const arabic = (await arabicRes.json()).data.text;
  const kurdish = (await kurdishRes.json()).data.text;

  const container = document.getElementById("content");
  container.className = "flex container";
  container.innerHTML = `
    <div class="ayah-box">
      <h2>سۆرە ${surah}، ئایەت ${ayah}</h2>
      <p class="arabic-text">
        <span>📜 عەرەبی:</span><br>${arabic}
      </p>
      <p class="kurdish-text">
        <span>🔍 کوردی:</span><br>${kurdish}
      </p>
      <div>
        <audio controls>
          <source src="https://everyayah.com/data/Nasser_Alqatami_128kbps/${String(surah).padStart(3, '0')}${String(ayah).padStart(3, '0')}.mp3" type="audio/mp3" />
          Your browser does not support the audio element.
        </audio>
      </div>
      <br />
      <button onclick="showQuran()" class="back-button">⬅️ گەڕانەوە بۆ سۆرەکان</button>
    </div>
  `;
}

async function showHadith() {
  const res = await fetch("hadith.json");
  const hadiths = await res.json();

  const container = document.getElementById("content");
  container.innerHTML = "<h2>بەشی حدیث هەڵبژێرە</h2>";
  container.className = "grid container";

  hadiths.forEach(h => {
    const btn = document.createElement("button");
    btn.textContent = `حدیث ${h.id}`;
    btn.className = "button";
    btn.onclick = () => {
      container.className = "flex container";
      container.innerHTML = `
        <div class="hadith-box">
          <h3>📜 حدیث ${h.id}</h3>
          <p class="arabic-text">
            <span>عەرەبی:</span><br>${h.hadith_ar}
          </p>
          <p class="kurdish-text">
            <span>کوردی:</span><br>${h.hadith_ku}
          </p>
          <p><strong>Sahih:</strong> ${h.hadith_sahih}</p>
          <p><strong>Explanation:</strong> ${h.hadith_geranawa}</p>
          <br />
          <button onclick="showHadith()" class="back-button">⬅️ گەڕانەوە</button>
        </div>
      `;
    };
    container.appendChild(btn);
  });
}

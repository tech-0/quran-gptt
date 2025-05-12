async function showQuran() {
  const res = await fetch("https://api.alquran.cloud/v1/surah");
  const data = await res.json();

  const surahs = data.data;
  const container = document.getElementById("content");
  container.setAttribute("dir", "rtl");
  container.className = "grid gap-4 md:grid-cols-2 lg:grid-cols-6 text-[15px]";
  container.innerHTML = "<h2 class='col-span-full text-center text-2xl font-semibold mb-6'>سورەیەک هەلبژێرە</h2>";

  surahs.forEach(s => {
    const btn = document.createElement("button");
    btn.textContent = `${s.number}: ${s.name}`;
    btn.classList.add(
      "bg-indigo-600",
      "text-white",
      "p-4",
      "rounded-xl",
      "shadow-sm",
      "hover:bg-indigo-500",
      "hover:shadow-md",
      "transition",
      "duration-200",
      "text-[15px]",
      "font-medium",
      "w-full"
    );
    btn.onclick = () => showAyahs(s.number, s.name, s.numberOfAyahs);
    container.appendChild(btn);
  });
}

async function showAyahs(surah, name, count) {
  const container = document.getElementById("content");
  container.setAttribute("dir", "rtl");
  container.className = "grid gap-4 md:grid-cols-2 lg:grid-cols-6 text-[15px]";
  container.innerHTML = `<h2 class="col-span-full text-center text-2xl font-semibold mb-6">${name} - ئایەت هەلبژێرە</h2>`;

  for (let i = 1; i <= count; i++) {
    const btn = document.createElement("button");
    btn.textContent = `ئایەت ${i}`;
    btn.classList.add(
      "bg-indigo-600",
      "text-white",
      "p-4",
      "rounded-xl",
      "shadow-sm",
      "hover:bg-indigo-500",
      "hover:shadow-md",
      "transition",
      "duration-200",
      "text-[15px]",
      "font-medium",
      "w-full"
    );
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
  container.setAttribute("dir", "rtl");
  container.className = "flex justify-center text-[15px]";
  container.innerHTML = `
    <div class="bg-white p-6 sm:p-8 rounded-2xl shadow-xl max-w-3xl w-full text-center">
      <h2 class="text-2xl font-bold text-indigo-700 mb-6">سورە ${surah}, ئایەت ${ayah}</h2>
      <p class="mb-4 text-right text-2xl text-gray-900 leading-loose border-b pb-4 border-gray-200">
        <span class="block text-teal-600 font-semibold">📜 عەرەبی:</span>
        ${arabic}
      </p>
      <p class="mb-4 text-right text-lg text-gray-800 leading-relaxed border-b pb-4 border-gray-200">
        <span class="block text-green-700 font-semibold">🔍 کوردی:</span>
        ${kurdish}
      </p>
      <div class="mt-4 mb-6">
        <audio controls class="w-full rounded-lg border border-gray-300">
          <source src="https://everyayah.com/data/Nasser_Alqatami_128kbps/${String(surah).padStart(3, '0')}${String(ayah).padStart(3, '0')}.mp3" type="audio/mp3" />
          Your browser does not support the audio element.
        </audio>
      </div>
      <button onclick="showQuran()" class="bg-gray-600 text-white py-2 px-6 rounded-lg hover:bg-gray-500 transition text-[15px]">⬅️ گەڕانەوە</button>
    </div>
  `;
}

async function showHadith() {
  const res = await fetch("hadith.json");
  const hadiths = await res.json();

  const container = document.getElementById("content");
  container.setAttribute("dir", "rtl");
  container.className = "grid gap-4 md:grid-cols-2 lg:grid-cols-3 text-[15px]";
  container.innerHTML = "<h2 class='col-span-full text-center text-2xl font-semibold mb-6'>حدیثێک هەلبژێرە</h2>";

  hadiths.forEach(h => {
    const btn = document.createElement("button");
    btn.textContent = `حدیث ${h.id}`;
    btn.classList.add(
      "bg-purple-500",
      "text-white",
      "p-4",
      "rounded-xl",
      "shadow",
      "hover:bg-purple-400",
      "transition",
      "duration-200",
      "text-[15px]",
      "font-medium",
      "w-full"
    );
    btn.onclick = () => {
      container.setAttribute("dir", "rtl");
      container.className = "flex justify-center text-[15px]";
      container.innerHTML = `
        <div class="bg-white p-6 sm:p-8 rounded-2xl shadow-xl max-w-3xl w-full text-center">
          <h3 class="text-center text-2xl font-semibold mb-4">📜 حدیث ${h.id}</h3>
          <p class="mb-4 text-right text-xl text-gray-900 leading-loose border-b pb-4 border-gray-200">
            <span class="block text-purple-700 font-semibold">عەرەبی:</span>
            ${h.hadith_ar}
          </p>
          <p class="mb-4 text-right text-lg text-gray-800 leading-relaxed border-b pb-4 border-gray-200">
            <span class="block text-green-600 font-semibold">کوردی:</span>
            ${h.hadith_ku}
          </p>
          <p class="mb-2 text-right"><strong>سەحیح:</strong> ${h.hadith_sahih}</p>
          <p class="mb-4 text-right"><strong>وەسف:</strong> ${h.hadith_geranawa}</p>
          <button onclick="showHadith()" class="bg-gray-600 text-white py-2 px-6 rounded-lg hover:bg-gray-500 transition text-[15px]">⬅️ گەڕانەوە</button>
        </div>
      `;
    };
    container.appendChild(btn);
  });
}

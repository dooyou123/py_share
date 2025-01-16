document
  .getElementById("handoverForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const date = document.getElementById("date").value;
    const shift = document.getElementById("shift").value;
    const notes = document.getElementById("notes").value;
    const created = new Date().toISOString(); // Get current time in ISO format
    document.getElementById("created").value = created;

    const response = await fetch("/add_entry", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, date, shift, notes, created }),
    });

    if (response.ok) {
      alert("데이터를 작성했습니다!");
      loadEntries();
    } else {
      alert("데이터 작성에 실패했습니다.");
    }
  });

async function loadEntries() {
  const response = await fetch("/get_entries");
  const entries = await response.json();

  entries.reverse();

  const entryList = document.getElementById("entryList");
  entryList.innerHTML = ""; // 기존 데이터를 초기화

  entries.forEach((entry) => {
    const entryDiv = document.createElement("div");
    entryDiv.className = "entry";
    entryDiv.setAttribute("data-id", entry.id); // 고유한 id를 data-id에 저장

    // created 값에서 날짜와 시간 추출
    const createdDateTime = formatDateTime(entry.created);

    entryDiv.innerHTML = `
        <p><strong>${entry.name}</strong> (${entry.date}</strong> - ${entry.shift}조) / 작성시각: ${createdDateTime} </p>
        <p>${entry.notes}</p>
        <button onclick="deleteEntry(${entry.id})" class="delete-btn">삭제</button>
      `;

    entryList.appendChild(entryDiv);
  });
}

// 날짜와 시간 형식을 반환하는 함수
function formatDateTime(dateString) {
  const date = new Date(dateString); // 문자열을 Date 객체로 변환

  const year = date.getFullYear(); // 연도
  const month = String(date.getMonth() + 1).padStart(2, "0"); // 월
  const day = String(date.getDate()).padStart(2, "0"); // 일

  const hours = String(date.getHours()).padStart(2, "0"); // 시
  const minutes = String(date.getMinutes()).padStart(2, "0"); // 분
  const seconds = String(date.getSeconds()).padStart(2, "0"); // 초

  // 연/월/일 시간:분:초 형식으로 반환
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

document.getElementById("search-button").addEventListener("click", function () {
  const searchTerm = document
    .getElementById("search-input")
    .value.toLowerCase();
  filterEntries(searchTerm);
});

document.getElementById("search-input").addEventListener("input", function () {
  // 입력할 때마다 검색
  const searchTerm = document
    .getElementById("search-input")
    .value.toLowerCase();
  filterEntries(searchTerm);
});

function filterEntries(searchTerm) {
  const entries = document.querySelectorAll("#entryList .entry"); // 모든 항목 선택

  entries.forEach((entry) => {
    const entryText = entry.textContent.toLowerCase(); // 항목의 텍스트 내용 가져오기

    // 이름, 날짜, 쉬프트, 내용 등을 포함한 검색
    if (
      entryText.includes(searchTerm) ||
      entry.querySelector("p").textContent.toLowerCase().includes(searchTerm)
    ) {
      entry.style.display = "block"; // 검색어 포함 시 표시
    } else {
      entry.style.display = "none"; // 검색어 미포함 시 숨김
    }
  });
}

async function deleteEntry(id) {
  if (confirm("내용을 삭제하시겠습니까?")) {
      const response = await fetch("/delete_entry", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({ id }), // 고유 id를 서버로 전송
      });

      if (response.ok) {
          alert("데이터를 삭제했습니다!");
          loadEntries(); // 삭제 후 데이터 재로딩
      } else {
          alert("데이터 삭제를 실패했습니다.");
      }
  }
}

loadEntries();

function updateClock() {
  const now = new Date();

  // 날짜 정보 가져오기 (요일 포함)
  const dateString = now.toLocaleDateString("ko-KR", {
    year: "numeric", // 필요하다면 년도 표시
    month: "2-digit",
    day: "2-digit",
    weekday: "short", // 짧은 요일 이름 (예: "월", "화", "수")
  });

  // 시간 정보 가져오기 (기존 코드와 동일)
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const seconds = now.getSeconds().toString().padStart(2, "0");

  // 날짜와 시간을 조합하여 문자열 생성
  const timeString = `${dateString} ${hours}:${minutes}:${seconds}`;

  document.getElementById("clock").textContent = timeString;
}

// 페이지 로드 시 시계 업데이트
updateClock();

// 1초마다 시계 업데이트
setInterval(updateClock, 1000);

const versionMeta = document.querySelector('meta[name="version"]');
const lastUpdatedMeta = document.querySelector('meta[name="last-updated"]');

if (versionMeta && lastUpdatedMeta) {
  const version = versionMeta.getAttribute("content");
  const lastUpdated = lastUpdatedMeta.getAttribute("content");
  document.getElementById(
    "footer-version"
  ).textContent = `Last Updated: ${lastUpdated} | v${version}`;
} else {
  // 메타 태그가 없을 경우 기본 메시지 표시 (선택적)
  document.getElementById("footer-version").textContent = "버전 정보 없음";
}

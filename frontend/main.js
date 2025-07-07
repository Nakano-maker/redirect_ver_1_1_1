// 要素取得
const clockElement = document.getElementById("clock");
const infoElement = document.getElementById("info");
const numberElement = document.getElementById("wait-number");
const statusElement = document.getElementById("status");
const logoElement = document.getElementById("logo");
const redirectElement = document.getElementById("redirecting");

// 時計更新
function updateClock() {
  const now = new Date();
  const formatted = now.toLocaleTimeString("ja-JP", { hour12: false });
  clockElement.textContent = formatted;
}
setInterval(updateClock, 1000);
updateClock(); // 初回実行

// API確認と表示切替
function checkAccessStatus() {
  fetch("/access")
    .then(res => res.json())
    .then(data => {
      console.log("取得データ:", data); // デバッグ用

      if (data.redirectUrl) {
        // 入場可能
        statusElement.style.display = "none";
        logoElement.style.display = "none";
        infoElement.style.display = "none";
        numberElement.style.display = "none";
        redirectElement.style.display = "block";

        setTimeout(() => {
          window.location.href = data.redirectUrl;
        }, 2000);
      } else {
        // 待機中
        infoElement.style.display = "block";
        numberElement.style.display = "block";
        redirectElement.style.display = "none";

        numberElement.textContent = `順番待ち: ${data.waitNumber}番目`;
      }
    })
    .catch(err => {
      console.error("ERROR 01:", err);
      statusElement.innerHTML = `<h1 style="color:red;">ERROR 02</h1>`;
    });
}

// ポーリング実行
setInterval(checkAccessStatus, 5000);
checkAccessStatus(); // 初回実行
/**
 * ポモドーロタイマー JavaScript
 *
 * 機能:
 *  - 円形SVGプログレスバーのリアルタイムアニメーション
 *  - 残り時間に応じた色変化 (青 → 黄 → 赤)
 *  - 集中タイム中のパーティクルエフェクト
 *  - セッション開始/終了時の波紋エフェクト
 */

/* =====================================================
   定数 / 設定
   ===================================================== */
const RADIUS = 96;                          // SVGサークルの半径
const CIRCUMFERENCE = 2 * Math.PI * RADIUS; // 円周長

// 色定義 (R, G, B)
const COLOR_BLUE   = [33,  150, 243];
const COLOR_YELLOW = [255, 193,   7];
const COLOR_RED    = [244,  67,  54];

const MODES = {
  work:  { label: '集中タイム',   minutes: 25 },
  short: { label: '短い休憩',     minutes: 5  },
  long:  { label: '長い休憩',     minutes: 15 },
};

/* =====================================================
   状態管理
   ===================================================== */
let currentMode    = 'work';
let totalSeconds   = MODES.work.minutes * 60;
let remainSeconds  = totalSeconds;
let isRunning      = false;
let intervalId     = null;
let pomodoroCount  = 0;

/* =====================================================
   DOM 参照
   ===================================================== */
const progressCircle  = document.getElementById('progressCircle');
const timeDisplay     = document.getElementById('timeDisplay');
const sessionLabel    = document.getElementById('sessionLabel');
const startBtn        = document.getElementById('startBtn');
const resetBtn        = document.getElementById('resetBtn');
const pomodoroCountEl = document.getElementById('pomodoroCount');
const timerWrapper    = document.querySelector('.timer-wrapper');
const rippleOverlay   = document.getElementById('rippleOverlay');
const canvas          = document.getElementById('particleCanvas');
const ctx             = canvas.getContext('2d');

/* =====================================================
   初期化
   ===================================================== */
progressCircle.style.strokeDasharray  = CIRCUMFERENCE;
progressCircle.style.strokeDashoffset = 0;

resizeCanvas();
window.addEventListener('resize', resizeCanvas);

/* =====================================================
   ユーティリティ
   ===================================================== */

/** 2つのRGB配列を比率 t (0~1) で線形補間する */
function lerpColor(c1, c2, t) {
  const r = Math.round(c1[0] + (c2[0] - c1[0]) * t);
  const g = Math.round(c1[1] + (c2[1] - c1[1]) * t);
  const b = Math.round(c1[2] + (c2[2] - c1[2]) * t);
  return `rgb(${r},${g},${b})`;
}

/**
 * 残り時間の割合に応じた進捗色を計算する
 *   ratio=1.0: 青 (開始直後)
 *   ratio=0.5: 黄 (半分経過)
 *   ratio=0.0: 赤 (終了直前)
 */
function getProgressColor(ratio) {
  if (ratio > 0.5) {
    return lerpColor(COLOR_YELLOW, COLOR_BLUE, (ratio - 0.5) * 2);
  }
  return lerpColor(COLOR_RED, COLOR_YELLOW, ratio * 2);
}

/** 秒数を MM:SS 形式に変換する */
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

/* =====================================================
   UI 更新
   ===================================================== */

/** プログレスバーと時間表示を現在の remainSeconds で更新する */
function updateUI() {
  // 残り時間テキスト
  timeDisplay.textContent = formatTime(remainSeconds);

  // SVG プログレスバー (stroke-dashoffset)
  const ratio  = remainSeconds / totalSeconds;
  const offset = CIRCUMFERENCE * (1 - ratio);
  progressCircle.style.strokeDashoffset = offset;

  // 色変化
  const color = getProgressColor(ratio);
  progressCircle.style.stroke = color;

  // CSS カスタムプロパティ経由でボタン色も追従させる
  document.documentElement.style.setProperty('--progress-color', color);
}

/** モード切替後に UI をリセットする */
function resetUI() {
  totalSeconds  = MODES[currentMode].minutes * 60;
  remainSeconds = totalSeconds;
  sessionLabel.textContent = MODES[currentMode].label;
  updateUI();
}

/* =====================================================
   タイマー制御
   ===================================================== */

function startTimer() {
  if (isRunning) return;
  isRunning = true;
  startBtn.textContent = '⏸ 一時停止';
  startBtn.classList.add('paused');

  // 集中モードのみパーティクルを表示
  if (currentMode === 'work') {
    canvas.classList.add('active');
  }

  triggerRipple();

  intervalId = setInterval(() => {
    remainSeconds--;
    updateUI();

    if (remainSeconds <= 0) {
      completeSession();
    }
  }, 1000);
}

function pauseTimer() {
  if (!isRunning) return;
  isRunning = false;
  clearInterval(intervalId);
  startBtn.textContent = '▶ 再開';
  startBtn.classList.remove('paused');
  canvas.classList.remove('active');
}

function resetTimer() {
  pauseTimer();
  startBtn.textContent = '▶ スタート';
  canvas.classList.remove('active');
  resetUI();
}

function completeSession() {
  pauseTimer();
  startBtn.textContent = '▶ スタート';
  canvas.classList.remove('active');

  if (currentMode === 'work') {
    pomodoroCount++;
    pomodoroCountEl.textContent = pomodoroCount;
  }

  // 完了パルスアニメーション
  timerWrapper.classList.add('pulse');
  setTimeout(() => timerWrapper.classList.remove('pulse'), 1600);

  triggerRipple();
  resetUI();
}

/* =====================================================
   波紋 (Ripple) エフェクト
   ===================================================== */

function triggerRipple() {
  const colors = ['rgba(33,150,243,0.3)', 'rgba(255,193,7,0.2)', 'rgba(244,67,54,0.15)'];
  colors.forEach((color, i) => {
    setTimeout(() => {
      const el = document.createElement('div');
      el.className = 'ripple';
      const size = 80;
      const cx   = window.innerWidth  / 2;
      const cy   = window.innerHeight / 2;
      el.style.cssText = `
        width:${size}px; height:${size}px;
        left:${cx - size / 2}px; top:${cy - size / 2}px;
        background:${color};
      `;
      rippleOverlay.appendChild(el);
      setTimeout(() => el.remove(), 2000);
    }, i * 200);
  });
}

/* =====================================================
   パーティクルエフェクト (Canvas)
   ===================================================== */

function resizeCanvas() {
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
}

/** パーティクル1粒 */
class Particle {
  constructor() {
    this.reset();
  }

  reset() {
    this.x     = Math.random() * canvas.width;
    this.y     = canvas.height + 10;
    this.size  = Math.random() * 3 + 1;
    this.speedY = Math.random() * 1.2 + 0.4;
    this.speedX = (Math.random() - 0.5) * 0.6;
    this.opacity = Math.random() * 0.6 + 0.2;
    this.hue   = Math.floor(Math.random() * 60) + 200; // 青〜紫系
  }

  update() {
    this.y -= this.speedY;
    this.x += this.speedX;
    this.opacity -= 0.003;
    if (this.y < -10 || this.opacity <= 0) {
      this.reset();
    }
  }

  draw() {
    ctx.save();
    ctx.globalAlpha = this.opacity;
    ctx.fillStyle   = `hsl(${this.hue}, 80%, 65%)`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

const PARTICLE_COUNT = 80;
const particles = Array.from({ length: PARTICLE_COUNT }, () => new Particle());

function animateParticles() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (canvas.classList.contains('active')) {
    particles.forEach(p => { p.update(); p.draw(); });
  }
  requestAnimationFrame(animateParticles);
}

animateParticles();

/* =====================================================
   イベントリスナー
   ===================================================== */

startBtn.addEventListener('click', () => {
  if (isRunning) {
    pauseTimer();
  } else {
    startTimer();
  }
});

resetBtn.addEventListener('click', resetTimer);

document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentMode = btn.dataset.mode;
    resetTimer();
  });
});

/* =====================================================
   初回 UI 描画
   ===================================================== */
updateUI();

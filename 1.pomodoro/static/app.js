// ポモドーロタイマー - メインロジック

class PomodoroTimer {
    constructor() {
        this.isRunning = false;
        this.isWorkMode = true;
        this.timeLeft = 25 * 60; // 秒単位
        this.totalTime = 25 * 60;
        this.timerInterval = null;
        this.audioContext = null;
        
        // 設定のデフォルト値
        this.settings = {
            work_minutes: 25,
            break_minutes: 5,
            theme: 'dark',
            sound_start: true,
            sound_end: true,
            sound_tick: false
        };
        
        this.initElements();
        this.initProgressRing();
        this.loadSettings();
        this.attachEventListeners();
    }
    
    initElements() {
        this.timerDisplay = document.getElementById('timer');
        this.modeDisplay = document.getElementById('mode');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        
        // 設定要素
        this.workMinutesSelect = document.getElementById('workMinutes');
        this.breakMinutesSelect = document.getElementById('breakMinutes');
        this.themeSelect = document.getElementById('theme');
        this.soundStartCheckbox = document.getElementById('soundStart');
        this.soundEndCheckbox = document.getElementById('soundEnd');
        this.soundTickCheckbox = document.getElementById('soundTick');
        this.saveSettingsBtn = document.getElementById('saveSettings');
        
        // プログレスリング
        this.progressCircle = document.querySelector('.progress-ring-circle');
    }
    
    initProgressRing() {
        const radius = this.progressCircle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        this.progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
        this.progressCircle.style.strokeDashoffset = 0;
        this.circumference = circumference;
    }
    
    attachEventListeners() {
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.themeSelect.addEventListener('change', () => this.changeTheme());
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (response.ok) {
                this.settings = await response.json();
                this.applySettings();
            }
        } catch (error) {
            console.error('設定の読み込みに失敗しました:', error);
        }
    }
    
    applySettings() {
        // フォームに設定を反映
        this.workMinutesSelect.value = this.settings.work_minutes;
        this.breakMinutesSelect.value = this.settings.break_minutes;
        this.themeSelect.value = this.settings.theme;
        this.soundStartCheckbox.checked = this.settings.sound_start;
        this.soundEndCheckbox.checked = this.settings.sound_end;
        this.soundTickCheckbox.checked = this.settings.sound_tick;
        
        // テーマを適用
        this.changeTheme();
        
        // タイマーをリセット
        this.reset();
    }
    
    async saveSettings() {
        const newSettings = {
            work_minutes: parseInt(this.workMinutesSelect.value),
            break_minutes: parseInt(this.breakMinutesSelect.value),
            theme: this.themeSelect.value,
            sound_start: this.soundStartCheckbox.checked,
            sound_end: this.soundEndCheckbox.checked,
            sound_tick: this.soundTickCheckbox.checked
        };
        
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newSettings)
            });
            
            if (response.ok) {
                this.settings = await response.json();
                this.applySettings();
                this.showNotification('設定を保存しました');
            } else {
                this.showNotification('設定の保存に失敗しました', 'error');
            }
        } catch (error) {
            console.error('設定の保存に失敗しました:', error);
            this.showNotification('設定の保存に失敗しました', 'error');
        }
    }
    
    changeTheme() {
        const body = document.body;
        body.className = `theme-${this.themeSelect.value}`;
    }
    
    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            
            if (this.settings.sound_start) {
                this.playSound('start');
            }
            
            this.timerInterval = setInterval(() => this.tick(), 1000);
        }
    }
    
    pause() {
        if (this.isRunning) {
            this.isRunning = false;
            this.startBtn.disabled = false;
            this.pauseBtn.disabled = true;
            clearInterval(this.timerInterval);
        }
    }
    
    reset() {
        this.pause();
        this.isWorkMode = true;
        this.timeLeft = this.settings.work_minutes * 60;
        this.totalTime = this.settings.work_minutes * 60;
        this.updateDisplay();
        this.updateMode();
        this.updateProgressRing();
    }
    
    tick() {
        if (this.settings.sound_tick) {
            this.playSound('tick');
        }
        
        this.timeLeft--;
        
        if (this.timeLeft < 0) {
            this.timerComplete();
        } else {
            this.updateDisplay();
            this.updateProgressRing();
        }
    }
    
    timerComplete() {
        this.pause();
        
        if (this.settings.sound_end) {
            this.playSound('end');
        }
        
        // モードを切り替え
        this.isWorkMode = !this.isWorkMode;
        
        if (this.isWorkMode) {
            this.timeLeft = this.settings.work_minutes * 60;
            this.totalTime = this.settings.work_minutes * 60;
        } else {
            this.timeLeft = this.settings.break_minutes * 60;
            this.totalTime = this.settings.break_minutes * 60;
        }
        
        this.updateDisplay();
        this.updateMode();
        this.updateProgressRing();
        
        this.showNotification(
            this.isWorkMode ? '作業時間です！' : '休憩時間です！'
        );
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.timerDisplay.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    updateMode() {
        this.modeDisplay.textContent = this.isWorkMode ? '作業時間' : '休憩時間';
    }
    
    updateProgressRing() {
        const progress = this.timeLeft / this.totalTime;
        const offset = this.circumference - (progress * this.circumference);
        this.progressCircle.style.strokeDashoffset = offset;
    }
    
    playSound(type) {
        // Web Audio APIを使って音を生成
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        // 音の種類に応じて周波数と長さを変更
        switch (type) {
            case 'start':
                oscillator.frequency.value = 523.25; // C5
                gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + 0.3);
                break;
            case 'end':
                // 2音のビープ
                oscillator.frequency.value = 659.25; // E5
                gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + 0.2);
                
                // 2つ目の音
                setTimeout(() => {
                    const osc2 = this.audioContext.createOscillator();
                    const gain2 = this.audioContext.createGain();
                    osc2.connect(gain2);
                    gain2.connect(this.audioContext.destination);
                    osc2.frequency.value = 783.99; // G5
                    gain2.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    osc2.start(this.audioContext.currentTime);
                    osc2.stop(this.audioContext.currentTime + 0.3);
                }, 200);
                break;
            case 'tick':
                oscillator.frequency.value = 1000; // 1kHz
                gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05);
                oscillator.start(this.audioContext.currentTime);
                oscillator.stop(this.audioContext.currentTime + 0.05);
                break;
        }
    }
    
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 1000;
            padding: 12px 20px; border-radius: 8px; font-weight: bold;
            background: ${type === 'error' ? '#e74c3c' : '#27ae60'};
            color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: opacity 0.5s;
        `;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 500);
        }, 2000);
    }
}

// アプリ起動
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});

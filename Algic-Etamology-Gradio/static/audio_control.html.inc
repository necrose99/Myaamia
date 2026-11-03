<!-- static/audio_control.html.inc -->
<div class="audio-profile-panel" style="background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 0.85rem; margin-bottom: 0.85rem;">
  <div class="pt" style="margin-bottom: 0.5rem;"><span class="dot" style="background: var(--accent);"></span>Audiological Voice Matrix</div>
  
  <label for="kilahkwaani-voice-selector" style="font-size: 0.75rem; font-family: var(--mono); color: var(--muted); display: block; margin-bottom: 0.25rem;">
    Perceptual Profile (6-Inflections):
  </label>
  
  <select id="kilahkwaani-voice-selector" onchange="Kilahkwaani.setAudiologicalProfile(this.value)" style="margin-bottom: 0.4rem;">
    <option value="balanced_neutral" selected>Standard Neutral (Balanced Matrix)</option>
    <option value="bill_bass">"Bill" — Low-Pass Deep Bass (High-Freq Loss Fallback)</option>
    <option value="gregory_mid">"Gregory" — Enhanced Mid-Range Clear Baritone</option>
    <option value="mitch_middle">"Mitch in the Middle" — Balanced Medial Delivery</option>
    <option value="sally_treble">"Sally" — High-Clarity Treble (Low-Freq Loss Fallback)</option>
    <option value="susan_alto">"Susan" — Balanced Alto Profile</option>
    <option value="grovel_slow">"Grovel" — Ultra-Slow Cadence / Distinct Intonation</option>
  </select>
  
  <small style="font-family: var(--mono); font-size: 0.58rem; color: var(--muted); display: block; line-height: 1.3;">
    Adjusts both SpeechSynthesisUtterance parameters and native Web Audio filter nodes seamlessly.
  </small>
</div>

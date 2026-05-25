<template>
  <div class="app">
    <header>
      <h1>VISIT<span>S</span></h1>
      <span class="total">{{ stats.total ?? '—' }} total</span>
    </header>

    <div class="grid">
      <div class="card">
        <div class="card-title">Top Pages</div>
        <div class="bar-list">
          <div v-if="!stats.top_pages?.length" class="empty">no data</div>
          <div v-for="p in stats.top_pages" :key="p.path" class="bar-row">
            <span class="bar-label">{{ p.path }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: barWidth(p.count) + '%' }"></div>
            </div>
            <span class="bar-count">{{ p.count }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Last 24h by Hour</div>
        <div class="chart">
          <div v-if="!stats.by_hour?.length" class="empty">no data</div>
          <div v-for="h in hours" :key="h.hour" class="col">
            <div class="col-bar" :style="{ height: colHeight(h.count) + '%' }"></div>
            <div class="col-label">{{ h.hour }}</div>
          </div>
        </div>
      </div>
    </div>

    <button class="track-btn" @click="track">Track Visit</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8080'
const stats = ref({})

async function load() {
  const r = await fetch(`${API}/stats`)
  stats.value = await r.json()
}

async function track() {
  await fetch(`${API}/track?path=/dashboard`)
  await load()
}

const hours = computed(() => {
  const map = {}
  ;(stats.value.by_hour || []).forEach(h => { map[h.hour] = h.count })
  return Array.from({ length: 24 }, (_, i) => ({ hour: i, count: map[i] || 0 }))
})

const maxCount = computed(() => Math.max(...(stats.value.top_pages || []).map(p => p.count), 1))
const maxHour = computed(() => Math.max(...hours.value.map(h => h.count), 1))

function barWidth(n) { return Math.round((n / maxCount.value) * 100) }
function colHeight(n) { return Math.round((n / maxHour.value) * 100) }

let timer
onMounted(() => { load(); timer = setInterval(load, 5000) })
onUnmounted(() => clearInterval(timer))
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'IBM Plex Mono', monospace;
  background: #0e0e0e;
  color: #e8e8e8;
  min-height: 100vh;
  padding: 40px 20px;
}

.app { max-width: 900px; margin: 0 auto; }

header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 32px;
}
h1 { font-size: 28px; font-weight: 600; letter-spacing: -1px; }
h1 span { color: #c8ff00; }
.total { color: #555; font-size: 13px; }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }

.card {
  background: #1a1a1a;
  border: 1px solid #2e2e2e;
  padding: 20px;
}
.card-title { font-size: 11px; color: #555; margin-bottom: 16px; letter-spacing: 1px; text-transform: uppercase; }

.bar-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 12px; }
.bar-label { width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #aaa; }
.bar-track { flex: 1; height: 4px; background: #2e2e2e; }
.bar-fill { height: 100%; background: #c8ff00; transition: width .3s; }
.bar-count { width: 30px; text-align: right; color: #555; }

.chart { display: flex; align-items: flex-end; gap: 3px; height: 100px; }
.col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 4px; }
.col-bar { width: 100%; background: #00e5ff; min-height: 2px; transition: height .3s; }
.col-label { font-size: 9px; color: #444; }

.empty { color: #444; font-size: 12px; }

.track-btn {
  background: #c8ff00;
  color: #000;
  border: none;
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  padding: 12px 24px;
  cursor: pointer;
}
.track-btn:hover { opacity: .85; }
</style>

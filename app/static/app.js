const $ = (sel) => document.querySelector(sel);
const api = {
  async health(){ const r = await fetch('/api/v1/health'); return r.json(); },
  async listSensors(q){ const r = await fetch('/api/v1/sensor-data' + (q?`?q=${encodeURIComponent(q)}`:'')); return r.json(); },
  async getSensor(id){ const r = await fetch('/api/v1/sensor-data/'+id); if(!r.ok) throw new Error('Not found'); return r.json(); },
  async createSensor(data){ const r = await fetch('/api/v1/sensor-data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error('Create failed'); return r.json(); },
  async updateSensor(id,data){ const r = await fetch('/api/v1/sensor-data/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error('Update failed'); return r.json(); },
  async delSensor(id){ const r = await fetch('/api/v1/sensor-data/'+id,{method:'DELETE'}); if(!r.ok) throw new Error('Delete failed'); return true; },
  async getWatering(deviceId = 'autogrow_esp32'){ const r = await fetch('/api/v1/watering/' + deviceId); if(!r.ok) throw new Error('Get watering failed'); return r.json(); },
  async updateWatering(data){ const r = await fetch('/api/v1/watering',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error('Update watering failed'); return r.json(); },
  async listWateringHistory(deviceId){ const r = await fetch('/api/v1/watering-history' + (deviceId?`?device_id=${encodeURIComponent(deviceId)}`:'')); return r.json(); },
  async getWateringHistory(id){ const r = await fetch('/api/v1/watering-history/'+id); if(!r.ok) throw new Error('Not found'); return r.json(); },
  async createWateringHistory(data){ const r = await fetch('/api/v1/watering-history',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error('Create failed'); return r.json(); },
  async updateWateringHistory(id,data){ const r = await fetch('/api/v1/watering-history/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error('Update failed'); return r.json(); },
  async delWateringHistory(id){ const r = await fetch('/api/v1/watering-history/'+id,{method:'DELETE'}); if(!r.ok) throw new Error('Delete failed'); return true; },
};

async function refreshHealth(){
  try{
    const h = await api.health();
    $('#health').textContent = 'API: ' + (h.status || 'unknown');
  }catch(e){ $('#health').textContent = 'API: offline'; }
}

function formatDateTime(dateStr){
  return new Date(dateStr).toLocaleString();
}

function formatTemperature(temp){
  return `${temp.toFixed(1)}°C`;
}

function formatHumidity(hum){
  return `${hum.toFixed(1)}%`;
}

function formatLux(lux){
  return `${lux} lux`;
}

function formatPumpStatus(pump, wateringData){
  // Use watering data if available, otherwise use sensor data
  const isActive = wateringData ? wateringData.pump_active : pump;
  return isActive ? '🟢 Active' : '🔴 Inactive';
}

function formatWateringDuration(seconds){
  if (seconds < 60) {
    return `${seconds}s`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }
}

function formatWateringType(autoWatering){
  return autoWatering ? '🤖 Auto' : '👤 Manual';
}

function formatWateringStatus(wateringEnded){
  return wateringEnded ? '✅ Complete' : '🔄 In Progress';
}


async function updateLatestReadings(sensors){
  if(sensors.length === 0) return;
  
  const latest = sensors[0];
  $('#latest-temp').textContent = formatTemperature(latest.temperature);
  $('#latest-humidity').textContent = formatHumidity(latest.humidity);
  $('#latest-lux').textContent = formatLux(latest.lux);
  $('#latest-device').textContent = latest.device_id || 'Unknown';
  
  // Fetch watering data and update pump status
  try {
    const wateringData = await api.getWatering();
    $('#latest-pump').textContent = formatPumpStatus(latest.pump_active, wateringData);
  } catch (error) {
    console.error('Failed to load watering data:', error);
    // Fallback to sensor data if watering data fails
    $('#latest-pump').textContent = formatPumpStatus(latest.pump_active, null);
  }
}

function rowHtml(sensor){
  const created = formatDateTime(sensor.created_at);
  const deviceId = sensor.device_id || 'Unknown';
  const firmware = sensor.firmware_version || 'N/A';
  const sensorType = sensor.sensor_type || 'N/A';
  return `<tr>
    <td>${sensor.id}</td>
    <td>${formatTemperature(sensor.temperature)}</td>
    <td>${formatHumidity(sensor.humidity)}</td>
    <td>${formatLux(sensor.lux)}</td>
    <td>${formatPumpStatus(sensor.pump_active)}</td>
    <td>${deviceId}</td>
    <td><span class="muted">${firmware}</span></td>
    <td><span class="muted">${sensorType}</span></td>
    <td><span class="muted">${created}</span></td>
    <td class="actions-col">
      <button class="danger" data-del="${sensor.id}">Delete</button>
    </td>
  </tr>`;
}

function wateringRowHtml(watering){
  const started = formatDateTime(watering.watering_started);
  const ended = watering.watering_ended ? formatDateTime(watering.watering_ended) : '--';
  const deviceId = watering.device_id || 'Unknown';
  return `<tr>
    <td>${watering.id}</td>
    <td>${deviceId}</td>
    <td>${formatWateringDuration(watering.watering_duration)}</td>
    <td>${formatWateringType(watering.auto_watering)}</td>
    <td><span class="muted">${started}</span></td>
    <td><span class="muted">${ended}</span></td>
    <td>${formatWateringStatus(watering.watering_ended)}</td>
    <td class="actions-col">
      <button class="danger" data-del-watering="${watering.id}">Delete</button>
    </td>
  </tr>`;
}

async function loadTable(q){
  try {
    const sensors = await api.listSensors(q);
    $('#sensor-table tbody').innerHTML = sensors.map(rowHtml).join('');
    await updateLatestReadings(sensors);
  } catch (error) {
    console.error('Failed to load sensor data:', error);
    $('#sensor-table tbody').innerHTML = '<tr><td colspan="10" class="error">Failed to load data</td></tr>';
  }
}

async function loadWateringTable(deviceId){
  try {
    const wateringHistory = await api.listWateringHistory(deviceId);
    $('#watering-table tbody').innerHTML = wateringHistory.map(wateringRowHtml).join('');
  } catch (error) {
    console.error('Failed to load watering history:', error);
    $('#watering-table tbody').innerHTML = '<tr><td colspan="8" class="error">Failed to load data</td></tr>';
  }
}

function getUniqueDevices(sensors){
  const deviceMap = new Map();
  
  sensors.forEach(sensor => {
    const deviceId = sensor.device_id || 'Unknown';
    if (!deviceMap.has(deviceId) || new Date(sensor.created_at) > new Date(deviceMap.get(deviceId).created_at)) {
      deviceMap.set(deviceId, sensor);
    }
  });
  
  return Array.from(deviceMap.values()).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

function deviceCardHtml(device, wateringData = null){
  const deviceId = device.device_id || 'Unknown';
  const firmware = device.firmware_version || 'N/A';
  const sensorType = device.sensor_type || 'N/A';
  const lastUpdate = formatDateTime(device.created_at);
  
  // Use watering data for pump status if available and device matches
  const pumpStatus = (wateringData && wateringData.device_id === deviceId) 
    ? formatPumpStatus(device.pump_active, wateringData)
    : formatPumpStatus(device.pump_active, null);
  
  return `
    <div class="device-card">
      <div class="device-header">
        <h3 class="device-name">${deviceId}</h3>
        <span class="device-meta">${firmware} • ${sensorType}</span>
      </div>
      <div class="device-readings">
        <div class="device-reading">
          <span class="device-reading-label">🌡️</span>
          <span class="device-reading-value">${formatTemperature(device.temperature)}</span>
        </div>
        <div class="device-reading">
          <span class="device-reading-label">💧</span>
          <span class="device-reading-value">${formatHumidity(device.humidity)}</span>
        </div>
        <div class="device-reading">
          <span class="device-reading-label">☀️</span>
          <span class="device-reading-value">${formatLux(device.lux)}</span>
        </div>
        <div class="device-reading">
          <span class="device-reading-label">🔧</span>
          <span class="device-reading-value">${pumpStatus}</span>
        </div>
      </div>
      <div class="device-footer">
        <span class="device-updated">Updated: ${lastUpdate}</span>
      </div>
    </div>
  `;
}

async function loadDeviceOverview(){
  try {
    const sensors = await api.listSensors();
    const uniqueDevices = getUniqueDevices(sensors);
    
    if (uniqueDevices.length === 0) {
      $('#device-overview').innerHTML = '<div class="no-data">No device data available</div>';
      return;
    }
    
    // Fetch watering data for all devices
    let wateringData = null;
    try {
      wateringData = await api.getWatering();
    } catch (error) {
      console.error('Failed to load watering data for device overview:', error);
    }
    
    $('#device-overview').innerHTML = uniqueDevices.map(device => deviceCardHtml(device, wateringData)).join('');
  } catch (error) {
    console.error('Failed to load device overview:', error);
    $('#device-overview').innerHTML = '<div class="error">Failed to load device data</div>';
  }
}


document.addEventListener('click', async (e) => {
  const delId = e.target.getAttribute('data-del');
  const delWateringId = e.target.getAttribute('data-del-watering');
  
  if(delId){
    if(confirm('Delete sensor reading #' + delId + '?')){
      try {
        await api.delSensor(delId);
        await loadTable($('#search').value.trim());
      } catch (error) {
        alert('Failed to delete sensor data');
      }
    }
  }else if(delWateringId){
    if(confirm('Delete watering record #' + delWateringId + '?')){
      try {
        await api.delWateringHistory(delWateringId);
        await loadWateringTable($('#watering-search').value.trim());
      } catch (error) {
        alert('Failed to delete watering history');
      }
    }
  }
});


$('#search').addEventListener('input', async (e) => {
  await loadTable(e.target.value.trim());
});

$('#refresh-btn').addEventListener('click', async () => {
  await loadTable($('#search').value.trim());
});

$('#watering-search').addEventListener('input', (e) => {
  loadWateringTable(e.target.value.trim());
});

$('#watering-refresh-btn').addEventListener('click', async () => {
  await loadWateringTable($('#watering-search').value.trim());
});

// Auto-refresh sensor data every 30 seconds
setInterval(async () => {
  await loadTable($('#search').value.trim());
  await loadDeviceOverview();
}, 30000);

// Auto-refresh pump status (including watering data) every 5 seconds (more frequent for real-time updates)
setInterval(async () => {
  try {
    // Get latest sensor data to ensure we have the most recent pump status
    const sensors = await api.listSensors();
    if (sensors.length > 0) {
      const latest = sensors[0];
      const wateringData = await api.getWatering();
      $('#latest-pump').textContent = formatPumpStatus(latest.pump_active, wateringData);
      
      // Also refresh device overview pump status
      await loadDeviceOverview();
    }
  } catch (error) {
    console.error('Failed to refresh pump/watering status:', error);
  }
}, 5000);

(async function init(){
  await refreshHealth();
  await loadTable();
  await loadDeviceOverview();
  await loadWateringTable();
})();
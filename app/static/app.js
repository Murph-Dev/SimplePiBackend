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

function formatPumpStatus(pump){
  return pump ? '🟢 Active' : '🔴 Inactive';
}

function formatWateringStatus(wateringData){
  if (!wateringData) return '--';
  
  const now = new Date();
  const lastWatering = wateringData.last_watering ? new Date(wateringData.last_watering) : null;
  
  let status = wateringData.pump_active ? '💧 Watering' : '⏸️ Idle';
  
  if (lastWatering) {
    const diffMinutes = Math.floor((now - lastWatering) / (1000 * 60));
    if (diffMinutes < 60) {
      status += ` (${diffMinutes}m ago)`;
    } else {
      const diffHours = Math.floor(diffMinutes / 60);
      status += ` (${diffHours}h ago)`;
    }
  }
  
  return status;
}

async function updateLatestReadings(sensors){
  if(sensors.length === 0) return;
  
  const latest = sensors[0];
  $('#latest-temp').textContent = formatTemperature(latest.temperature);
  $('#latest-humidity').textContent = formatHumidity(latest.humidity);
  $('#latest-lux').textContent = formatLux(latest.lux);
  $('#latest-pump').textContent = formatPumpStatus(latest.pump_active);
  
  // Update watering status
  try {
    const wateringData = await api.getWatering();
    $('#latest-watering').textContent = formatWateringStatus(wateringData);
  } catch (error) {
    console.error('Failed to load watering data:', error);
    $('#latest-watering').textContent = 'Error';
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
      <button data-edit="${sensor.id}">Edit</button>
      <button class="danger" data-del="${sensor.id}">Delete</button>
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

function formData(){
  const tempRaw = $('#sensor-temp').value;
  const humidityRaw = $('#sensor-humidity').value;
  const luxRaw = $('#sensor-lux').value;
  const pump = $('#sensor-pump').checked;
  const device = $('#sensor-device').value.trim() || null;
  const timestampRaw = $('#sensor-timestamp').value;
  const firmware = $('#sensor-firmware').value.trim() || null;
  const sensorType = $('#sensor-type').value.trim() || null;
  
  const temperature = tempRaw === '' ? null : Number(tempRaw);
  const humidity = humidityRaw === '' ? null : Number(humidityRaw);
  const lux = luxRaw === '' ? null : Number(luxRaw);
  const timestamp = timestampRaw === '' ? null : Number(timestampRaw);
  
  return { temperature, humidity, lux, pump_active: pump, device_id: device, timestamp, firmware_version: firmware, sensor_type: sensorType };
}

function resetForm(){
  $('#sensor-id').value = '';
  $('#sensor-temp').value = '';
  $('#sensor-humidity').value = '';
  $('#sensor-lux').value = '';
  $('#sensor-pump').checked = false;
  $('#sensor-device').value = '';
  $('#sensor-timestamp').value = '';
  $('#sensor-firmware').value = '';
  $('#sensor-type').value = '';
}

function populateForm(sensor){
  $('#sensor-id').value = sensor.id;
  $('#sensor-temp').value = sensor.temperature;
  $('#sensor-humidity').value = sensor.humidity;
  $('#sensor-lux').value = sensor.lux;
  $('#sensor-pump').checked = sensor.pump_active;
  $('#sensor-device').value = sensor.device_id || '';
  $('#sensor-timestamp').value = sensor.timestamp || '';
  $('#sensor-firmware').value = sensor.firmware_version || '';
  $('#sensor-type').value = sensor.sensor_type || '';
}

document.addEventListener('click', async (e) => {
  const editId = e.target.getAttribute('data-edit');
  const delId = e.target.getAttribute('data-del');
  
  if(editId){
    try {
      const sensor = await api.getSensor(editId);
      populateForm(sensor);
    } catch (error) {
      alert('Failed to load sensor data');
    }
  }else if(delId){
    if(confirm('Delete sensor reading #' + delId + '?')){
      try {
        await api.delSensor(delId);
        await loadTable($('#search').value.trim());
        resetForm();
      } catch (error) {
        alert('Failed to delete sensor data');
      }
    }
  }
});

$('#sensor-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = $('#sensor-id').value;
  const payload = formData();
  
  // Validate required fields
  if(payload.temperature === null || payload.humidity === null || payload.lux === null){
    alert('Temperature, humidity, and light level are required');
    return;
  }
  
  try {
    if(id){
      await api.updateSensor(id, payload);
    }else{
      await api.createSensor(payload);
    }
    await loadTable($('#search').value.trim());
    resetForm();
  } catch (error) {
    alert('Failed to save sensor data');
  }
});

$('#reset-btn').addEventListener('click', resetForm);

$('#search').addEventListener('input', async (e) => {
  await loadTable(e.target.value.trim());
});

$('#refresh-btn').addEventListener('click', async () => {
  await loadTable($('#search').value.trim());
});

// Auto-refresh sensor data every 30 seconds
setInterval(async () => {
  await loadTable($('#search').value.trim());
}, 30000);

// Auto-refresh watering status every 5 seconds (more frequent for real-time updates)
setInterval(async () => {
  try {
    const wateringData = await api.getWatering();
    $('#latest-watering').textContent = formatWateringStatus(wateringData);
  } catch (error) {
    console.error('Failed to refresh watering data:', error);
  }
}, 5000);

(async function init(){
  await refreshHealth();
  await loadTable();
})();
// ============================================================
// UI/i18n/patch.js  —  NUEVO. Cargar DESPUÉS de los 7 idiomas y ANTES de app.js.
// Añade las claves que faltaban en I18N_DATA (run.status.*, dev.*, device.os
// con template, sidebar.toggle) para que ningún widget muestre la clave cruda.
// ============================================================
window.I18N_DATA = window.I18N_DATA || {};
(function (D) {
  const add = (lang, obj) => { D[lang] = Object.assign(D[lang] || {}, obj); };
  const runStatus = (idle, running, done, error, cancelled) => ({
    'run.status.idle': idle, 'run.status.running': running, 'run.status.done': done,
    'run.status.error': error, 'run.status.cancelled': cancelled
  });
  const dev = (none, unknown, error, connected, android) => ({
    'dev.none': none, 'dev.unknown': unknown, 'dev.error': error,
    'dev.connected': connected, 'dev.android': android, 'device.os': android
  });
  add('en', Object.assign(runStatus('Idle', 'Running', 'Done', 'Error', 'Cancelled'),
    dev('No device', 'Unknown', 'Error', 'Connected', 'Android {0}'), { 'sidebar.toggle': 'Toggle sidebar' }));
  add('es', Object.assign(runStatus('En reposo', 'Ejecutando', 'Completado', 'Error', 'Cancelado'),
    dev('Sin dispositivo', 'Desconocido', 'Error', 'Conectado', 'Android {0}'), { 'sidebar.toggle': 'Alternar menú' }));
  add('id', Object.assign(runStatus('Siaga', 'Berjalan', 'Selesai', 'Error', 'Dibatalkan'),
    dev('Tidak ada perangkat', 'Tidak diketahui', 'Error', 'Terhubung', 'Android {0}'), { 'sidebar.toggle': 'Alihkan bilah sisi' }));
  add('pt', Object.assign(runStatus('Em repouso', 'Executando', 'Concluído', 'Erro', 'Cancelado'),
    dev('Sem dispositivo', 'Desconhecido', 'Erro', 'Conectado', 'Android {0}'), { 'sidebar.toggle': 'Alternar barra lateral' }));
  add('th', Object.assign(runStatus('ว่าง', 'กำลังทำงาน', 'เสร็จสิ้น', 'ข้อผิดพลาด', 'ยกเลิก'),
    dev('ไม่มีอุปกรณ์', 'ไม่ทราบ', 'ข้อผิดพลาด', 'เชื่อมต่อแล้ว', 'Android {0}'), { 'sidebar.toggle': 'สลับแถบด้านข้าง' }));
  add('ur', Object.assign(runStatus('غیر فعال', 'جاری', 'مکمل', 'خرابی', 'منسوخ'),
    dev('کوئی ڈیوائس نہیں', 'نامعلوم', 'خرابی', 'منسلک', 'Android {0}'), { 'sidebar.toggle': 'سائیڈبار ٹوگل کریں' }));
  add('vi', Object.assign(runStatus('Nghỉ', 'Đang chạy', 'Hoàn thành', 'Lỗi', 'Đã hủy'),
    dev('Không có thiết bị', 'Không xác định', 'Lỗi', 'Đã kết nối', 'Android {0}'), { 'sidebar.toggle': 'Chuyển đổi thanh bên' }));
})(window.I18N_DATA);

function getConfig_() {
  const p = PropertiesService.getScriptProperties();
  return {
    url: p.getProperty('CLOUD_RUN_URL'),
    key: p.getProperty('APP_API_KEY'),
    recipients: p.getProperty('RECIPIENTS')
  };
}

function fetchReport_(cadence) {
  const c = getConfig_();
  const response = UrlFetchApp.fetch(c.url + '/report?cadence=' + encodeURIComponent(cadence), {
    method: 'get', headers: {'X-API-Key': c.key}, muteHttpExceptions: true
  });
  if (response.getResponseCode() !== 200) throw new Error(response.getContentText());
  return JSON.parse(response.getContentText());
}

function sendFlash_(cadence) {
  const c = getConfig_();
  const r = fetchReport_(cadence);
  const inlineImages = {};
  Object.keys(r.images || {}).forEach(function(cid) {
    inlineImages[cid] = Utilities.newBlob(Utilities.base64Decode(r.images[cid]), 'image/png', cid + '.png');
  });
  GmailApp.sendEmail(c.recipients, r.subject, 'Please view this email in HTML.', {
    htmlBody: r.html_body,
    inlineImages: inlineImages,
    name: 'Traya Retail Intelligence'
  });
}

function sendWeeklyFlash() { sendFlash_('weekly'); }
function sendDailyFlash() { sendFlash_('daily'); }
function testWeeklyFlash() { sendWeeklyFlash(); }

function createWeeklyTrigger() {
  deleteTriggers_('sendWeeklyFlash');
  ScriptApp.newTrigger('sendWeeklyFlash').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(8).inTimezone('Asia/Kolkata').create();
}

function createDailyTrigger() {
  deleteTriggers_('sendDailyFlash');
  ScriptApp.newTrigger('sendDailyFlash').timeBased().everyDays(1).atHour(20).inTimezone('Asia/Kolkata').create();
}

function deleteTriggers_(handler) {
  ScriptApp.getProjectTriggers().forEach(function(t) { if (t.getHandlerFunction() === handler) ScriptApp.deleteTrigger(t); });
}

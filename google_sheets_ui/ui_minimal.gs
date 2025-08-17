const REPORT_SHEET_NAME = 'Rotation Report';

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🏋️ Adaptive Training System')
    .addItem('👁️ View Rotation Report', 'viewReport')
    .addSeparator()
    .addItem('📋 View Exercise Families', 'showExerciseFamilies')
    .addToUi();
}

function viewReport() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(REPORT_SHEET_NAME);
  if (sh) { ss.setActiveSheet(sh); }
  else {
    SpreadsheetApp.getUi().alert(
      'Report Not Found',
      `The "${REPORT_SHEET_NAME}" sheet has not been generated yet.`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}

function showExerciseFamilies() {
  const lines = [
    '🔄 EXERCISE FAMILIES', '',
    'This info is maintained by the backend and used for analysis.',
    'See the Python file backend/families.py for the full list.'
  ];
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(REPORT_SHEET_NAME) || ss.insertSheet(REPORT_SHEET_NAME);
  sh.clear();
  sh.getRange(1,1).setValue('📋 Exercise Families').setFontWeight('bold');
  sh.getRange(3,1,lines.length,1).setValues(lines.map(s => [s]));
  ss.setActiveSheet(sh);
}

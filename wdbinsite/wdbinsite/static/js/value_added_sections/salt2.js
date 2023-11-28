function addSectionSalt2(addToDivId, jsonURL, imageBucket) {
  $.ajax({
    dataType: "json",
    url: jsonURL,
    success: function (data) {
      let mostRecentAlert = data['data'][0]['alert_id'];

      let sectionDiv = buildSalt2SectionDiv();
      let fitImage = buildSalt2Image(mostRecentAlert, imageBucket);
      sectionDiv.appendChild(fitImage);

      let fitsTable = buildSalt2Table(jsonURL);
      sectionDiv.appendChild(fitsTable);

      document.getElementById(addToDivId).appendChild(sectionDiv);

    }
  });
}

function buildSalt2SectionDiv() {
  // Create a new div to hold Salt2 related elements
  let sectionDiv = document.createElement('div');
  sectionDiv.classList.add('value-added-section');
  sectionDiv.id = 'salt2-value-added';

  // Wrapper div for styling headers
  let headerDiv = document.createElement('div');
  headerDiv.classList.add('section-header');

  // Section header
  let header = document.createElement('h3');
  header.textContent = 'Salt2 Supernova Fit';

  headerDiv.appendChild(header);
  sectionDiv.appendChild(headerDiv);
  return sectionDiv;
}

function buildSalt2Image(alertId, imageBucket) {
  let img = document.createElement("IMG");
  img.src = 'https://storage.googleapis.com/' + imageBucket + '/salt2/plot_lc/candid_' + alertId + '.png';
  img.alt = '';
  return img;
}

function buildSalt2Table(jsonURL) {
  let colNames = [
    'Alert Id', 'Chisq', 'NDOF', 'z', 'z Err', 't0', 't0 Err', 'x0', 'x0 Err', 'x1', 'x1 Err', 'c', 'c Err'
  ];

  // Create an empty table object
  let fitResultTable = document.createElement('table');
  fitResultTable.classList.add("table");
  fitResultTable.classList.add("table-striped");
  fitResultTable.id = 'salt2-fits-table';

  // Add table header values
  let thead = fitResultTable.createTHead();
  let row = thead.insertRow();
  for (let colNameText of colNames) {
    let th = document.createElement("th");
    let text = document.createTextNode(colNameText);
    th.appendChild(text);
    row.appendChild(th);
  }

  populateSalt2Table(fitResultTable, jsonURL);
  return fitResultTable;
}

function populateSalt2Table(table, jsonURL) {
  $(document).ready(function () {
    $('#' + table.id).DataTable({
      searching: false,
      processing: true,
      serverSide: true,
      ajax: jsonURL,
      lengthChange: false,
      paging: false,
      bInfo: false,
      columns: [
        {"data": "alert_id"},
        {"data": "chisq"},
        {"data": "ndof"},
        {"data": "z"},
        {"data": "z_err"},
        {"data": "t0"},
        {"data": "t0_err"},
        {"data": "x0"},
        {"data": "x0_err"},
        {"data": "x1"},
        {"data": "x1_err"},
        {"data": "c"},
        {"data": "c_err"}
      ]
    });
  });
}

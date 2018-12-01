//global section
var setCellText2;
var postReportInfo2;
var sectionDrawn = false;
var section_width = 10;
var section_height = 6;
var start_cell, end_cell;
var sheet_;
var report_fields = {};
report_fields.dimension = report_fields.measure = "none";
//
(
	function(){
        Office.initialize = function (reason) {
            $(document).ready(function () {
//            $('#add').click(setColor);
            });
    };

    function postReportInfo(fields_dict) {
        var request = new XMLHttpRequest();
        request.open("POST", "/fields/");
        request.send(JSON.stringify(report_fields));
    }
    postReportInfo2 = postReportInfo;

    //param: Sheet1!E2
    function getSectionRange(initial_address) {
        if (sectionDrawn == true) return initial_address;

        var i = initial_address.indexOf("!");
        sheet_ = initial_address.substring(0, i);
        var add = initial_address.substring(i + 1);
        var letter = add[0];
        var num = add.substring(1);
        var start_cell_y = String(parseInt(num) -1);
        start_cell = letter + start_cell_y;
        var end_cell_x = String.fromCharCode(letter.charCodeAt() + section_width - 1);
        var end_cell_y = String(parseInt(num) + section_height - 2);
        console.log(`start :${add}`);
        end_cell = end_cell_x + end_cell_y
        console.log(`finally, end : ${end_cell}, sheet: ${sheet_}`)

        return sheet_+"!"+start_cell+":" + end_cell;
    };

    function setSectionBorder(context,range) {
        if (sectionDrawn == true) return;
        sectionDrawn = true;

        range.format.borders.getItem("EdgeBottom").style = "DashDot";
        range.format.borders.getItem('EdgeLeft').style = 'DashDot';
        range.format.borders.getItem('EdgeRight').style = 'DashDot';
        range.format.borders.getItem('EdgeTop').style = 'DashDot';

        var first_row = range.getRow(0);
        first_row.format.borders.getItem("EdgeBottom").style = "Double";
//        context.sync().then(function(){
//                console.log("border format done!")
//            }
//        );
    };

    //Todo: currently range is only a CELL!!!
    function getCellAbove(sheet, range) {
        var address = range.address;
        var num = String(parseInt(address[8]) - 1);
        var new_address = address.substring(0, 8) + num;
        console.log(`field name display at ${new_address}`);
        return sheet.getRange(new_address);
    }
    function setCellText(text) {
        Excel.run(function (context) {
            console.log("Info: add " + text);
            var range = context.workbook.getSelectedRange();
            //range.format.fill.color = 'green';
            //Todo: Only one cell can be selected
            range.formulas = [["=iaGet(\"" + text +"\")"]];
            range.format.autofitColumns();

            range.load("address");

            if (report_fields.dimension == "none")
                report_fields.dimension = text;
            else
                report_fields.measure = text;
            return context.sync()
            .then(function(){
                console.log(`Info: range address: "${range.address}"`);
                var section = getSectionRange(range.address);
                var sheet = context.workbook.worksheets.getItem(sheet_);

                var field_name_range = getCellAbove(sheet, range);
                field_name_range.values = [[text]];
                field_name_range.format.autofitColumns();

                var section_range = sheet.getRange(section);
                //section_range.format.fill.color = 'green';
                setSectionBorder(context, section_range);
                console.log("border section done!!!");
            })
            ;
        }).catch(function (error) {
            console.log("Error: " + error);
            if (error instanceof OfficeExtension.Error) {
                console.log("Debug info: " + JSON.stringify(error.debugInfo));
            }
        });
    }
    setCellText2 = setCellText;
})();


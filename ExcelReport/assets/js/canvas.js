var canvas = null;
var context = null;
var x_grid_offset = 20;
var y_grid_offset = 20;
var x_grid_num = 10;
var y_grid_num = 10;
var grid_width = -1;
var grid_height = -1;
var cell_width = -1;
var cell_height = -1;

class selectionArea {
    constructor(x, y, x_num, y_num) {
        if (x <= 0) x = 1;
        this.x = x;
        if (y <= 0) y = 1;
        this.y = y;

        if (x_num <= 0) x_num = 1;
        else if (x_num > x_grid_num) x_num = x_grid_num;
        this.x_num = x_num;

        if (y_num <= 0) y_num = 1;
        else if (y_num > y_grid_num) y_num = y_grid_num;
        this.y_num = y_num;
    }
}

var sa = null

function offsetToChar(offset) {
    var A = 'A'
    var num = A.charCodeAt() + offset
    var ret = String.fromCharCode(num)
    return ret
};

function initParameters(canvas_, context_) {
    canvas = canvas_;
    context = context_;
    grid_width = canvas.width - 2 * x_grid_offset;
    grid_height = canvas.height - 2 * y_grid_offset;

    cell_width = grid_width/(x_grid_num + 1);
    cell_height = grid_height/(y_grid_num + 1);
    console.log(`cell height ${cell_height}`)
}
function drawGridBorder(context) {
    console.log("draw grid border");
    context.save();

    context.lineWidth = 1;
    context.strokeStyle = 'black';
    context.beginPath()
    context.moveTo(x_grid_offset, y_grid_offset);
    context.lineTo(x_grid_offset + grid_width, y_grid_offset);
    context.lineTo(x_grid_offset + grid_width, y_grid_offset + grid_height)
    context.lineTo(x_grid_offset, y_grid_offset + grid_height)
    context.closePath();
    context.stroke();

    context.restore();
};

function drawGridTopBar(context) {
    context.save()

    context.fillStyle = 'grey'
    context.beginPath();
    context.rect(x_grid_offset, y_grid_offset, grid_width, cell_height);
    context.globalAlpha = 0.3
    context.fill();

    context.font = "20px"
    context.globalAlpha = 1.0;
    context.fillStyle = "blue"
    for (var i = 0; i < x_grid_num; i ++) {
        var x = x_grid_offset + (i + 1) * cell_width + 5;
        context.fillText(offsetToChar(i), x, y_grid_offset + 15);
    }
    context.restore()
};

function drawGridLeftBar() {
    context.save()

    context.fillStyle = 'grey'
    context.beginPath();
    context.rect(x_grid_offset, y_grid_offset, cell_width, grid_height);
    context.globalAlpha = 0.3
    context.fill();

    context.globalAlpha = 1.0
    context.font = "20px"
    context.fillStyle = "blue"
    for (var j = 0; j < y_grid_num; j ++) {
        var y = y_grid_offset + (j + 1) * cell_height + 15;
        context.fillText(String(j+1), x_grid_offset + 5, y);
    }
    context.restore()
};

function drawInnerLines(context) {
    context.save();

    context.lineWidth = 1
    context.strokeStyle = 'black'
    context.setLineDash([2,2])

    for(var j = 0; j < y_grid_num; j++) {
//        context.beginPath();

        var y = y_grid_offset + (j + 1) * cell_height
        context.moveTo(x_grid_offset, y)
        context.lineTo(x_grid_offset + grid_width, y)

//        context.closePath();
        context.stroke();
    }

    for (var i = 0; i < x_grid_num; i++) {
        var x = x_grid_offset + (i + 1) * cell_width
        context.moveTo(x, y_grid_offset)
        context.lineTo(x, y_grid_offset + grid_height)

        context.stroke();
    }
    context.restore();
};

function setSelectionArea(x, y, x_num, y_num) {
    sa = new selectionArea(x, y, x_num, y_num);
//    drawSelectionArea(context, sa);
}
function drawSelectionArea(context, selection) {
    if (!sa) return
    context.save();

    var x = x_grid_offset + selection.x * cell_width;
    var y = y_grid_offset + selection.y * cell_height;
    var width = cell_width * sa.x_num;
    var height = cell_height * sa.y_num;

    context.beginPath();
    context.globalAlpha = 0.3
    context.rect(x, y, width, height);
    context.fillStyle='yellow'
    context.fill();
    context.lineWidth = 3;
    context.strokeStyle = 'green';

    context.stroke();

    context.restore();
};

function getColumnIndex(x){
    for (var i = 0; i <= x_grid_num; i++){
        if (x_grid_offset + i * cell_width <= x &&
         x_grid_offset + (i + 1) * cell_width >= x)

        return i;
    }
    return -1;
};

function getRowIndex(x) {
    for (var j = 0; j <= y_grid_num; j++) {
        if (y_grid_offset + j * cell_height <= y &&
        y_grid_offset + (j + 1)*cell_height >= y)
        return j;
    }
    return -1;
};

function drawGrid() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    drawGridBorder(context);
    drawInnerLines(context);
    drawGridTopBar(context);
    drawGridLeftBar(context);
    drawSelectionArea(context, sa);
};

//drawGrid();

function iaGet(field) {
    var ret = "[" + field + "]";
    return ret;
};

//var CustomFunctionMappings = {};
CustomFunctionMappings.iaGet = iaGet;
console.log("iaGet " + iaGet("bp"));
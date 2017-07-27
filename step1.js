
/** ildebeaute: Extract brands */

var Horseman = require('node-horseman')
var fs = require('fs')
var horseman = new Horseman()

horseman
    //.on('error', console.error)
    .open('http://iledebeaute.ru/brands')
    .exists('#headerSelectBrand option')
    .then(function(exists) {
        console.log('select->option exists')
    })
    .evaluate(function() {
        var brands = document.querySelectorAll('#headerSelectBrand option')
        return Array.prototype.map.call(brands, function(el) {
            var value = el.value.replace(/\//g, '')
            return value
        })
    })
    .then(function(brands) {
        var out = []
        for (var i=0;i<brands.length;++i) {
            if (brands[i] != '')
                out.push(brands[i])
        }
        return out
    })
    .then(function(brands) {
        fs.writeFile("brands.json", JSON.stringify(brands), function(err) {
            if (err) {
                return console.log(err)
            }

            console.log("The file was saved!")
            process.exit()
        })
    })

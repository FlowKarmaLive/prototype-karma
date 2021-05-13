
var cram_color = d3.scaleLinear(
    [0,11],
    ["hsl(0, 50%, 90%)", "hsl(360, 50%, 90%)"]
).interpolate(d3.interpolateHslLong)


const MINUTES = 3

function tim () {
    var i, body = d3.select('body'), h1 = d3.select('h1');
    for (i = 0; i < 12; i++) {
        var c = d3.hsl(cram_color(i))
        var c0 = c+"";
        c.h += 180;
        c.s += 0.4;
        body.transition()
            .delay(MINUTES * 5000 * i)
            .duration(MINUTES * 5000)
            .style('background-color', c0);
        h1.transition()
            .delay(MINUTES * 5000 * i)
            .duration(MINUTES * 5000)
            .style('color', c);
    }
}

$(function() {

    window.setInterval(tim, MINUTES * 60000);
    tim();
})
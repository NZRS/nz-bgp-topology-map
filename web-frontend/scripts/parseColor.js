/**!
 * @preserve $.parseColor
 * Copyright 2011 THEtheChad Elliott
 * Released under the MIT and GPL licenses.
 */


// Parse hex/rgb{a} color syntax.
// @input string
// @returns array [r,g,b{,o}]
parseColor = function(color) {

    var cache
      , p = parseInt // Use p as a byte saving reference to parseInt
      , color = color.replace(/\s\s*/g,'') // Remove all spaces
    ;//var
    
    // Checks for 6 digit hex and converts string to integer
    if (cache = /^#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})/.exec(color)) 
        cache = [p(cache[1], 16), p(cache[2], 16), p(cache[3], 16)];
        
    // Checks for 3 digit hex and converts string to integer
    else if (cache = /^#([\da-fA-F])([\da-fA-F])([\da-fA-F])/.exec(color))
        cache = [p(cache[1], 16) * 17, p(cache[2], 16) * 17, p(cache[3], 16) * 17];
        
    // Checks for rgba and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgba\(([\d]+),([\d]+),([\d]+),([\d]+|[\d]*.[\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3], +cache[4]];
        
    // Checks for rgb and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgb\(([\d]+),([\d]+),([\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3]];
        
    // Otherwise throw an exception to make debugging easier
    else throw Error(color + ' is not supported by parseColor');
    
    // Performs RGBA conversion by default
    isNaN(cache[3]) && (cache[3] = 1);
    
    // Adds or removes 4th value based on rgba support
    // Support is flipped twice to prevent erros if
    // it's not defined
    return cache.slice(0,4);
}

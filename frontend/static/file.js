var RENDERED_PLAIN_COLORIZED;
var RENDERED_BIBTEX;
var API_DATA;

var query = function (q) {
    $.get('/resolve', {'q': q})
        .done(function(data) {
            API_DATA = data;

            // rest these. they'll need to be recomputed.
            RENDERED_PLAIN_COLORIZED = null;
            RENDERED_BIBTEX = null;
            render_output_zone();
    });
};


var render_output_zone = function () {
    var fmt = $('#btn-toggle-format').text().trim()
    var outputzone = $('#output-zone')

    if (fmt == 'BibTeX') {
        if (RENDERED_BIBTEX == null)
            RENDERED_BIBTEX = build_bibtex(API_DATA);
        $('#output-zone').text(RENDERED_BIBTEX);
    } else {
        if (RENDERED_PLAIN_COLORIZED == null)
            RENDERED_PLAIN_COLORIZED = build_plain_colorized(API_DATA);
        outputzone.empty();
        outputzone.append(RENDERED_PLAIN_COLORIZED);
    }
};


var build_bibtex = function (data) {
    var zipper = [];

    // Filter out 'None' tags. Form zipper
    // which is list(zip(tokens, tags))
    for (var i = 0; i < data['tokens'].length; i++) {
        var tok = data['tokens'][i];
        var tag = data['tags'][i];
        if (tag == 'None') {
            continue;
        }
        zipper.push([tag, tok]);
    }


    // Chunk the zipper into contiguous runs of the same tag.
    var last_tag = null;
    var chunk_toks = [];   // final length n_runs.
    var chunk_tags = [];   // final length n_runs.
    // each chunk_toks[i] is a list of variable length, with the tokens
    // in that run of consecutive tag.
    for (var i = 0; i < zipper.length; i++) {
        var tag = zipper[i][0];
        var tok = zipper[i][1];
        if (tag == last_tag) {
            chunk_toks[chunk_toks.length-1].push(tok);
        } else {
            chunk_toks.push([tok])
            chunk_tags.push(tag);
        }

        last_tag = tag;
    }

    fields = {
        authors: [{}],
        title: [],
        journal: [],
        volume: [],
        year: [],
        issue: [],
        page: [],
    }
    for (var i = 0; i < chunk_toks.length; i++) {
        if (chunk_tags[i] == 'journ') {
            Array.prototype.push.apply(fields['journal'], chunk_toks[i]);
        } else if (chunk_tags[i] == 'title') {
            Array.prototype.push.apply(fields['title'], chunk_toks[i]);
        } else if (chunk_tags[i] == 'vol') {
            Array.prototype.push.apply(fields['volume'], chunk_toks[i]);
        } else if (chunk_tags[i] == 'year') {
            Array.prototype.push.apply(fields['year'], chunk_toks[i]);
        }  else if (chunk_tags[i] == 'page') {
            Array.prototype.push.apply(fields['page'], chunk_toks[i]);
        } else if (chunk_tags[i] == 'issue') {
            Array.prototype.push.apply(fields['issue'], chunk_toks[i]);
        } else if (chunk_tags[i] == 'given' || chunk_tags[i] == 'fam') {
            var authors = fields['authors'];
            if (Object.keys(authors[authors.length-1]).length == 2) {
                authors.push({});
            }
            var last_auth = authors[authors.length-1];
            last_auth[chunk_tags[i]] = chunk_toks[i];
        }
    }

    // format the author list
    var author_records = fields['authors'];
    var authors = [];
    for (var i = 0; i < author_records.length; i++) {
        var g = author_records[i]['given'];
        if (g === undefined)
            g = [];
        var f = author_records[i]['fam'];
        if (f === undefined)
            f = [];
        authors.push(join_tokens(g.concat(f)));
    }

    var author_list = authors.join(' and ');
    var citekey = 'citekey'
    if (author_records.length > 0) {
        citekey = author_records[0]['fam'] + join_tokens(fields['year'])
        if (fields['title'].length > 0)
            citekey += fields['title'][0]
    }

    var lines = ['@author{' + citekey];
    if (author_list.length > 0)
        lines.push('  author = {' + author_list + '}');
    if (fields['title'].length > 0)
        lines.push('  title = {' + join_tokens(fields['title']) + '}');
    if (fields['journal'].length > 0)
        lines.push('  journal = {' + join_tokens(fields['journal']) + '}');
    if (fields['year'].length > 0)
        lines.push('  year = {' + join_tokens(fields['year']) + '}');
    if (fields['volume'].length > 0)
        lines.push('  volume = {' + join_tokens(fields['volume']) + '}');
    if (fields['issue'].length > 0)
        lines.push('  issue= {' + join_tokens(fields['issue']) + '}');
    if (fields['page'].length > 0)
        lines.push('  page= {' + join_tokens(fields['page']) + '}');

    var bibtex_string = lines.join(',\n') + '\n}';
    return bibtex_string;

};

var join_tokens = function (tokens) {
    var out = [];
    for (i = 0; i < tokens.length; i++) {
        out.push(tokens[i]);
        if (i < tokens.length-1) {
            var tok1 = tokens[i+1];
            if (!_.contains(['?', ')', ';', ':', ',', '.'], tok1)) {
                out.push(' ')
            }
        }
    }
    return out.join('');
};

var build_plain_colorized = function (data) {
    // o = $('#output-zone');
    o = $('<div></div>');
    o.text('');
    var n = data['tokens'].length;
    for (var i = 0; i < n; i++) {
        var tok = data['tokens'][i];
        var tag = data['tags'][i];
        o.append($('<span></span>').text(tok).addClass(tag));

        if (tok[0] == '(') {
            continue;
        }

        if (i < n-1) {
            tok1 = data['tokens'][i+1];
            if (tok1 == ',' || tok1[0] == ')' || tok1 == ';' || tok1 == ':' ||
                tok1 == '?' || tok1 == '.') {
                continue;
            }

            o.append($('<span></span>').text(' '));
        }
    }

    return o.children();
};


$(function () {
    if (window.location.hash == '#bibtex') {
        $('#btn-toggle-format').text('BibTeX ').append('<span class="caret"></span>');
    } else if (window.location.hash == '#bibtex') {
        $('#btn-toggle-format').text('Plain ').append('<span class="caret"></span>');
    }

    // placeholder
    // $('#form-box').val('Baggiolini, M., Dewald, B. & Moser, B. Adv. Immunol. 55, 97-179 (1994)');

    var queryTimeOut;
    $("#form-box").keyup(function(){
        var that = this;
       // $(this).val($(this).val().replace(/\n/g, ' '));
       // if (event.keyCode == 13) {

           clearTimeout(queryTimeOut);
           setTimeout(function() {
               query($(that).val());
           }, 100);
       // }
    });


    $(".dropdown-menu li a").click(function() {
        var top = $(this).parents(".btn-group").find('.btn');
        top.text($(this).text() + ' ').append('<span class="caret"></span>');
        render_output_zone();
    });
});


var SelectText = function (element) {
    var doc = document
        , text = doc.getElementById(element)
        , range, selection
    ;
    if (doc.body.createTextRange) {
        range = document.body.createTextRange();
        range.moveToElementText(text);
        range.select();
    } else if (window.getSelection) {
        selection = window.getSelection();
        range = document.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
    }
};

/*jslint browser: true*/
/*global $, jQuery, alert, _*/
"use strict";

(function () {

    var RENDERED_PLAIN_COLORIZED,
        RENDERED_BIBTEX,
        API_DATA;

    /*
        Hit the server API.
    */
    function query(q) {
        $.get('/resolve', {'q': q})
            .done(function (data) {
                API_DATA = data;

                // reset these. they'll need to be recomputed.
                RENDERED_PLAIN_COLORIZED = null;
                RENDERED_BIBTEX = null;
                render_output_zone();
            });
    }

    /*
        Compute whatever represntation is supposed to be shown
        in the output box if necessary, and display it.
    */
    function render_output_zone() {
        var fmt = $('#btn-toggle-format').text().trim(),
            outputzone = $('#output-zone');

        if (fmt === 'BibTeX') {
            if (RENDERED_BIBTEX === null) {
                RENDERED_BIBTEX = build_bibtex(API_DATA);
            }
            $('#output-zone').text(RENDERED_BIBTEX);
        } else {
            if (RENDERED_PLAIN_COLORIZED === null) {
                RENDERED_PLAIN_COLORIZED = build_plain_colorized(API_DATA);
            }
            outputzone.empty();
            outputzone.append(RENDERED_PLAIN_COLORIZED);
        }
    }


    /*
        Build the (colored) plain text representation of the tokenized/tagged
        data returned from the API.
    */
    function build_plain_colorized(data) {
        var i,
            o = $('<div></div>'),
            n = data['tokens'].length,
            tok,
            tag;

        o.text('');
        for (i = 0; i < n; i += 1) {
            tok = data.tokens[i];
            tag = data.tags[i];
            o.append($('<span></span>').text(tok).addClass(tag));

            if (tok[0] !== '(' && i < n - 1) {
                if (!_.contains(['?', ')', ';', ':', ',', '.'], data.tokens[i + 1])) {
                    o.append($('<span></span>').text(' '));
                }
            }
        }

        return o.children();
    }


    /*
        Build a BibTeX representation (string) of the tokenized/tagged
        data returned from the API.
    */
    function build_bibtex(data) {
        // Chunk the zipper into contiguous runs of the same tag.
        var i,
            last_tag = null,
            chunk_toks = [],   // final length n_runs.
            chunk_tags = [];   // final length n_runs.

        var tok, tag;

        // each chunk_toks[i] is a list of variable length, with the tokens
        // in that run of consecutive tag.
        for (i = 0; i < data.tokens.length; i += 1) {
            tok = data.tokens[i];
            tag = data.tags[i];

            if (tag !== 'None') {
                if (tag === last_tag) {
                    chunk_toks[chunk_toks.length - 1].push(tok);
                } else {
                    chunk_toks.push([tok]);
                    chunk_tags.push(tag);
                }
            }
            last_tag = tag;
        }

        var fields = {
            authors: [{}],
            title: [],
            journal: [],
            volume: [],
            year: [],
            issue: [],
            page: [],
        };

        for (i = 0; i < chunk_toks.length; i += 1) {
            if (chunk_tags[i] === 'journ') {
                Array.prototype.push.apply(fields.journal, chunk_toks[i]);
            } else if (chunk_tags[i] === 'title') {
                Array.prototype.push.apply(fields.title, chunk_toks[i]);
            } else if (chunk_tags[i] === 'vol') {
                Array.prototype.push.apply(fields.volume, chunk_toks[i]);
            } else if (chunk_tags[i] === 'year') {
                Array.prototype.push.apply(fields.year, chunk_toks[i]);
            } else if (chunk_tags[i] === 'page') {
                Array.prototype.push.apply(fields.page, chunk_toks[i]);
            } else if (chunk_tags[i] === 'issue') {
                Array.prototype.push.apply(fields.issue, chunk_toks[i]);
            } else if (chunk_tags[i] === 'given' || chunk_tags[i] === 'fam') {
                var authors = fields.authors;
                if (Object.keys(authors[fields.authors.length - 1]).length === 2) {
                    authors.push({});
                }
                var last_auth = authors[authors.length - 1];
                last_auth[chunk_tags[i]] = chunk_toks[i];
            }
        }
        console.log(chunk_tags);
        console.log(chunk_toks);

        // format the author list
        var author_records = fields.authors,
            authors = [];
        for (i = 0; i < author_records.length; i += 1) {
            var g = author_records[i].given;
            var f = author_records[i].fam;

            if (g === undefined) {
                g = [];
            }

            if (f === undefined) {
                continue;
            }
            authors.push(join_tokens(g.concat(f)));
        }

        var author_list = authors.join(' and '),
            citekey = 'citekey';
        if (author_records.length > 0) {
            citekey = author_records[0].fam + join_tokens(fields.year);
            if (fields.title.length > 0) {
                citekey += fields.title[0];
            }
        }

        var lines = ['@author{' + citekey];
        if (author_list.length > 0) {
            lines.push('  author = {' + author_list + '}');
        }
        if (fields.title.length > 0) {
            lines.push('  title = {' + join_tokens(fields.title) + '}');
        }
        if (fields.journal.length > 0) {
            lines.push('  journal = {' + join_tokens(fields.journal) + '}');
        }
        if (fields.year.length > 0) {
            lines.push('  year = {' + join_tokens(fields.year) + '}');
        }
        if (fields.volume.length > 0) {
            lines.push('  volume = {' + join_tokens(fields.volume) + '}');
        }
        if (fields.issue.length > 0) {
            lines.push('  issue= {' + join_tokens(fields.issue) + '}');
        }
        if (fields.page.length > 0) {
            lines.push('  page= {' + join_tokens(fields.page) + '}');
        }

        var bibtex_string = lines.join(',\n') + '\n}';
        return bibtex_string;

    }

    /*
        Utility function to join tokens with whitespace.
    */
    function join_tokens(tokens) {
        var i,
            out = [];

        for (i = 0; i < tokens.length; i += 1) {
            out.push(tokens[i]);
            if (i < tokens.length - 1) {
                if (!_.contains(['?', ')', ';', ':', ',', '.'], tokens[i + 1])) {
                    out.push(' ')
                }
            }
        }
        return out.join('');
    }


    // main
    $(function () {
        if (window.location.hash == '#bibtex') {
            $('#btn-toggle-format').text('BibTeX ').append('<span class="caret"></span>');
        } else if (window.location.hash == '#plain') {
            $('#btn-toggle-format').text('Plain ').append('<span class="caret"></span>');
        }

        // show placeholder's output
        query($('#form-box').attr('placeholder'));

        var queryTimeOut;
        $("#form-box").keyup(function(){
            var that = this;
            clearTimeout(queryTimeOut);
            setTimeout(function() {
                query($(that).val());
            }, 100);
        });


        $(".dropdown-menu li a").click(function() {
            var top = $(this).parents(".btn-group").find('.btn');
            top.text($(this).text() + ' ').append('<span class="caret"></span>');
            render_output_zone();
        });
    });

})();

/* global CKEDITOR, AWS, Promise */
/* jshint esversion: 6 */

/*
 * (c) 2015
 * Originally developed by Chris Kiehl:
 * https://github.com/chriskiehl/Dropler
 *
 * (c) 2017
 * Modified by Nik Nyby for the Center for Teaching and Learning at
 * Columbia University.
 */
/* eslint-disable no-useless-escape */

CKEDITOR.plugins.add('awsimage', {
    init: function(editor) {
        // https://gist.github.com/mathewbyrne/1280286
        var slugify = function(text) {
            return text.toString().toLowerCase()
                .replace(/\s+/g, '-')           // Replace spaces with -
                .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
                .replace(/\-\-+/g, '-')         // Replace multiple - with single -
                .replace(/^-+/, '')             // Trim - from start of text
                .replace(/-+$/, '');            // Trim - from end of text
        };

        var getUniqueFilename = function(filename) {
            var split = filename.split('.');
            var extension = split.pop();
            var name = split.join('.');

            var date = slugify(new Date().toISOString());

            return name + date + '.' + extension;
        };

        var uploadS3 = function(file) {
            if (!file || !file.name) {
                return new Promise(function(resolve, reject) {
                    reject('No filename');
                });
            }

            var filename = getUniqueFilename(file.name);
            var settings = editor.config.awsimageConfig.settings;

            AWS.config.update({
                accessKeyId: settings.accessKeyId,
                secretAccessKey: settings.secretAccessKey
            });
            AWS.config.region = 'us-east-1';

            var bucket = new AWS.S3({params: {Bucket: settings.bucket}});
            var params = {
                Key: filename,
                ContentType: file.type,
                Body: file,
                ACL: 'public-read'
            };
            return new Promise(function(resolve, reject) {
                bucket.upload(params, function(err, data) {
                    if (!err) {
                        resolve(data.Location);
                    } else {
                        reject(err);
                    }
                });
            });
        };

        var backends = {
            s3: {
                upload: uploadS3,
                required: [
                    'bucket', 'accessKeyId','secretAccessKey', 'region'
                ],
                init: function() {
                    /* eslint-disable scanjs-rules/assign_to_src */
                    var script = document.createElement('script');
                    script.async = 1;
                    script.src =
                        'https://sdk.amazonaws.com/js/aws-sdk-2.10.0.min.js';
                    document.body.appendChild(script);
                    /* eslint-enable scanjs-rules/assign_to_src */
                }
            }
        };

        var checkRequirement = function(condition, message) {
            if (!condition) {
                throw Error(
                    'Assert failed' + (typeof message !== 'undefined' ?
                        ': ' + message : ''));
            }
        };

        var validateConfig = function() {
            var errorTemplate = 'DragDropUpload Error: ->';
            checkRequirement(
                editor.config.hasOwnProperty('awsimageConfig'),
                errorTemplate +
                    'Missing required awsimageConfig in CKEDITOR.config.js'
            );

            var backend = backends[editor.config.awsimageConfig.backend];

            var suppliedKeys = Object.keys(
                editor.config.awsimageConfig.settings);
            var requiredKeys = backend.required;

            var missing = requiredKeys.filter(function(key) {
                return suppliedKeys.indexOf(key) < 0;
            });

            if (missing.length > 0) {
                throw 'Invalid Config: Missing required keys: ' +
                    missing.join(', ');
            }
        };

        validateConfig();

        var backend = backends[editor.config.awsimageConfig.backend];
        backend.init();

        var doNothing = function(e) { };
        var orPopError = function(err) { alert(err); };

        var insertImage = function(src) {
            var e = editor.document.createElement('img', {
                attributes: {
                    'class': 'img-responsive',
                    'src': src
                }
            });
            editor.insertElement(e);
        };

        var dropHandler = function(e) {
            e.preventDefault();
            var file = e.dataTransfer.files[0];
            backend.upload(file).then(insertImage, orPopError);
        };

        var addHeaders = function(xhttp, headers) {
            for (var key in headers) {
                if (headers.hasOwnProperty(key)) {
                    xhttp.setRequestHeader(key, headers[key]);
                }
            }
        };

        // eslint-disable-next-line no-unused-vars
        var post = function(url, data, headers) {
            return new Promise(function(resolve, reject) {
                var xhttp    = new XMLHttpRequest();
                xhttp.open('POST', url);
                addHeaders(xhttp, headers);
                xhttp.onreadystatechange = function() {
                    if (xhttp.readyState === 4) {
                        if (xhttp.status === 200) {
                            // eslint-disable-next-line security/detect-non-literal-fs-filename
                            resolve(JSON.parse(xhttp.responseText).data.link);
                        } else {
                            reject(JSON.parse(xhttp.responseText));
                        }
                    }
                };
                xhttp.send(data);
            });
        };

        CKEDITOR.on('instanceReady', function() {
            var container = editor.container;
            var iframe = jQuery(container.$).find('iframe')[0];
            var iframeBase = iframe.contentDocument.querySelector('html');
            var iframeBody = iframeBase.querySelector('body');

            iframeBody.ondragover = doNothing;
            iframeBody.ondrop = dropHandler;

            var paddingToCenterBody =
                ((iframeBase.offsetWidth - iframeBody.offsetWidth) / 2) + 'px';
            iframeBase.style.height = '100%';
            iframeBase.style.width = '100%';
            iframeBase.style.overflowX = 'hidden';

            iframeBody.style.height = '100%';
            iframeBody.style.margin = '0';
            iframeBody.style.paddingLeft = paddingToCenterBody;
            iframeBody.style.paddingRight = paddingToCenterBody;
        });
    }
});

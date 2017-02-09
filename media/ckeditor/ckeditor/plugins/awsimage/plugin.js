CKEDITOR.plugins.add('awsimage', {
    init: function( editor ) {
        var uploadS3 = function(file) {
            var settings = editor.config.awsimageConfig.settings;
            AWS.config.update({accessKeyId: settings.accessKeyId, secretAccessKey: settings.secretAccessKey});
            AWS.config.region = 'us-east-1';

            var bucket = new AWS.S3({params: {Bucket: settings.bucket}});
            var params = {Key: file.name, ContentType: file.type, Body: file, ACL: "public-read"};
            return new Promise(function(resolve, reject) {
                bucket.upload(params, function (err, data) {
                    console.log('upload complete', err, data);
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
                    var script = document.createElement('script');
                    script.async = 1;
                    script.src = 'https://sdk.amazonaws.com/js/aws-sdk-2.10.0.min.js';
                    document.body.appendChild(script);
                }
            }
        };

        var checkRequirement = function(condition, message) {
            if (!condition)
                throw Error("Assert failed" + (typeof message !== "undefined" ? ": " + message : ""));
        };

        function validateConfig() {
            var errorTemplate = 'DragDropUpload Error: ->';
            checkRequirement(
                editor.config.hasOwnProperty('awsimageConfig'),
                errorTemplate + "Missing required awsimageConfig in CKEDITOR.config.js"
            );

            var backend = backends[editor.config.awsimageConfig.backend];

            var suppliedKeys = Object.keys(editor.config.awsimageConfig.settings);
            var requiredKeys = backend.required;

            var missing = requiredKeys.filter(function(key) {
                return suppliedKeys.indexOf(key) < 0
            });

            if (missing.length > 0) {
                throw 'Invalid Config: Missing required keys: ' + missing.join(', ')
            }
        }

        validateConfig();

        var backend = backends[editor.config.awsimageConfig.backend];
        backend.init();

        function doNothing(e) { }
        function orPopError(err) { alert(err) }

        var insertImage = function(href) {
            var elem = editor.document.createElement('img', {
                attributes: {
                    src: href
                }
            });

            // TODO: should only insertElement in active instance
            for (var key in CKEDITOR.instances) {
                CKEDITOR.instances[key].insertElement(elem);
            }
        }

        var dropHandler = function(e) {
            e.preventDefault();
            var file = e.dataTransfer.files[0];
            backend.upload(file).then(insertImage, orPopError);
        }

        function addHeaders(xhttp, headers) {
            for (var key in headers) {
                if (headers.hasOwnProperty(key)) {
                    xhttp.setRequestHeader(key, headers[key]);
                }
            }
        }

        function post(url, data, headers) {
            return new Promise(function(resolve, reject) {
                var xhttp    = new XMLHttpRequest();
                xhttp.open('POST', url);
                addHeaders(xhttp, headers);
                xhttp.onreadystatechange = function () {
                    if (xhttp.readyState === 4) {
                        if (xhttp.status === 200) {
                            resolve(JSON.parse(xhttp.responseText).data.link);
                        } else {
                            reject(JSON.parse(xhttp.responseText));
                        }
                    }
                };
                xhttp.send(data);
            });
        }

        CKEDITOR.on('instanceReady', function() {
            var iframeBase = document.querySelector('iframe').contentDocument.querySelector('html');
            var iframeBody = iframeBase.querySelector('body');

            iframeBody.ondragover = doNothing;
            iframeBody.ondrop = dropHandler;

            paddingToCenterBody = ((iframeBase.offsetWidth - iframeBody.offsetWidth) / 2) + 'px';
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

#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly API_DIR=$DOC_DIR/api
readonly SWAGGER_UI_VERSION=3.23.11

function convert_yaml_to_json {
    local yaml_spec=${1?ERROR: mandatory YAML spcificaiton file name is not provided}
    local py_code="import sys, yaml, json; json.dump(yaml.load(sys.stdin), sys.stdout, indent=4)"

    python -c "${py_code}" < $yaml_spec > ${yaml_spec//.yaml/.json}
}

function generate_api_documentation {
    local json_spec=${1//.yaml/.json}
    local html_spec=${1//.yaml/.html}
    local api_title=${1##*/}; api_title=${api_title%.yaml}

    cat > $html_spec <<EOF
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>$api_title</title>
        <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/$SWAGGER_UI_VERSION/swagger-ui.css" >
        <style>
            html {
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }
            *, *:before, *:after {
                box-sizing: inherit;
            }
            body {
                margin:0;
                background: #fafafa;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"/>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/$SWAGGER_UI_VERSION/swagger-ui-bundle.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/$SWAGGER_UI_VERSION/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                var spec = $(cat $json_spec);
                const ui = SwaggerUIBundle({
                    spec: spec,
                    dom_id: "#swagger-ui",
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                })
                window.ui = ui
            }
        </script>
    </body>
</html>
EOF
}

for api_spec in $API_DIR/*.yaml; do
    convert_yaml_to_json $api_spec
    generate_api_documentation $api_spec
done

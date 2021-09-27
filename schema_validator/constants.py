SCHEMA_REQUEST_ATTRIBUTE = "_schema_request_schema"
SCHEMA_RESPONSE_ATTRIBUTE = "_schema_response_schemas"
SCHEMA_QUERYSTRING_ATTRIBUTE = "_schema_querystring_schema"
SCHEMA_TAG_ATTRIBUTE = "_schema_tag_schemas"
REF_PREFIX = "#/components/schemas/"
IGNORE_METHODS = {"OPTIONS", "HEAD"}

SWAGGER_TEMPLATE = """
<head>
  <link type="text/css" rel="stylesheet" href="{{ swagger_css_url }}">
  <title>{{ title }}</title>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="{{ swagger_js_url }}"></script>
  <script>
    const ui = SwaggerUIBundle({
      deepLinking: true,
      dom_id: "#swagger-ui",
      layout: "BaseLayout",
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
      ],
      showExtensions: true,
      showCommonExtensions: true,
      url: "{{ openapi_path }}"
    });
  </script>
</body>
"""

SWAGGER_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.47.1/swagger-ui-bundle.js"
SWAGGER_CSS_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.47.1/swagger-ui.min.css"

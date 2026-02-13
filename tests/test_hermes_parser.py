from app.hermes import parse_availability


def test_parse_availability_from_ld_json():
    html = """
    <html><head>
    <script type=\"application/ld+json\">
    {
      \"@type\": \"ItemList\",
      \"itemListElement\": [
        {\"item\": {\"name\": \"Birkin 25\", \"offers\": {\"availability\": \"https://schema.org/InStock\"}}},
        {\"item\": {\"name\": \"Kelly 28\", \"offers\": {\"availability\": \"https://schema.org/OutOfStock\"}}}
      ]
    }
    </script>
    </head></html>
    """

    data = parse_availability(html)
    assert data["birkin 25"] is True
    assert data["kelly 28"] is False

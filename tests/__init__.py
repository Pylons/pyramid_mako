def dummy_mako_preprocessor(template, settings):
    # demo preprocessor function
    template = template.replace("Hello", settings.get('replace_Hello', ''))
    return template


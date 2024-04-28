def pre_mutation(context):
    line: str = context.current_source_line.strip()
    if line.startswith('logger.'):
        context.skip = True

    if context.filename == "main.py":
        context.skip = True

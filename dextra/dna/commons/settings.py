import dextra.dna.core as C

C.io.stream.DEFAULT_READING_OPTIONS['csv'] = {
    'header': True,
    'multiLine': True,
    'inferSchema': True,
    'escape': '"'
}

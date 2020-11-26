from pyspark.sql import functions as F


def confirming_word_as_bool(col: str) -> F.Column:
    """Translate a confirmation word into a boolean.

    Args:
        col: a spark frame column

    Returns:
        pyspark.Column<bool>

    """
    col = F.lower(col)
    return (F.when(col == 'yes', True)
            .when(col == 'no', False)
            .otherwise(None))

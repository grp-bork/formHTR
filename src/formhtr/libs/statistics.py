def compute_success_ratio(contents, artefacts):
    """Compute ratio between number identified regions and extra content

    Args:
        contents (list): list of identified regions
        artefacts (dict): artefact per service

    Returns:
        Dict with keys ``identified`` (int), ``artefacts`` (int), ``ratio`` (float).
    """
    num_of_identified = len(contents)
    max_artefacts = max([len(items) for items in artefacts.values()])
    ratio = num_of_identified/max(max_artefacts, 1) # to avoid division by zero
    return {'identified': num_of_identified, 
            'artefacts': max_artefacts, 
            'ratio': ratio}

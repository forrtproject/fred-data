# test script for osf_citation_from_url
source(here::here("R", "osf_citation.R"))
cat('--- Function test (tibble) ---\n')
try(print(osf_citation_from_url('https://osf.io/cwmb5/files/9hjxc', output='tibble')))
cat('\n--- Function test (apa) ---\n')
try(print(osf_citation_from_url('https://osf.io/cwmb5/files/9hjxc', output='apa')))

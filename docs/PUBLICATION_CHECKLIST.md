# Publication checklist

The executable repository structure is ready, but the following publication
metadata cannot be inferred safely from the files and must be supplied by the
research author.

## Required author decisions

- Choose a code and documentation license, confirm the copyright holders and
  year, and add a root `LICENSE` file.
- Add `CITATION.cff` with the author names and identifiers, repository title,
  preferred citation, release version, and paper title. Add the DOI only after
  it exists.
- Record the exact name, provider, version or access date, citation, license,
  redistribution permission, and source checksum for every raw image dataset.
- Decide which raw data can be redistributed, which needs access instructions,
  and which derived tables or models can be deposited in a research archive.

## Before a research release

1. Initialize this directory as its own Git repository or archive the complete
   active source tree together with its SHA-256 source manifest. Do not use a
   neighbouring repository as its identity.
2. Create and commit the license, citation metadata, dataset provenance
   records, and any permitted small validation fixtures.
3. Recreate Python 3.10.11 from the pinned environment and run the tests and
   input verification.
4. Execute each canonical pipeline with a stable run identifier.
5. Add platform and hardware records to the same run directory, inspect them
   for private identifiers, and finalize the result manifest.
6. Deposit immutable results, record the archive DOI and checksums, and cite
   the exact release rather than a mutable working directory.

Do not claim raw-data regeneration until the missing dataset identities,
licenses, grouping identifiers, and checksums listed in
[`DATA.md`](DATA.md) have been resolved.

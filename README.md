# tap-sunwave

`tap-sunwave` is a Singer tap for Sunwave.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| user_id | True     | None    | Email address of the user to authenticate with. |
| client_id | True     | None    | Client ID, obtained from Sunwave support staff. |
| client_secret | True     | None    | Client secret, obtained from Sunwave support staff. |
| clinic_id | True     | None    | Clinic ID, obtained by inspecting requests in the browser. |
| stream_maps | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config | False    | None    | User-defined config values to be used within map expressions. |
| faker_config | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an addtional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator |
| faker_config.locale | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization |
| flattening_enabled | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth | False    | None    | The max depth to flatten schemas. |
| batch_config | False    | None    | Configuration for BATCH message capabilities. |
| batch_config.encoding | False    | None    | Specifies the format and compression of the batch files. |
| batch_config.encoding.format | False    | None    | Format to use for batch files. |
| batch_config.encoding.compression | False    | None    | Compression format to use for batch files. |
| batch_config.storage | False    | None    | Defines the storage layer to use when writing batch files |
| batch_config.storage.root | False    | None    | Root path to use when writing batch files. |
| batch_config.storage.prefix | False    | None    | Prefix to use when writing batch files. |

A full list of supported settings and capabilities is available by running: `tap-sunwave --about`


A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-sunwave --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

Provide your email address in config as `user_id`. Reach out to Sunwave support staff to get your `client_id` and `client_secret` (see instructions at https://emr.sunwavehealth.com/SunwaveEMR/swagger/).


## Usage

You can easily run `tap-sunwave` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-sunwave --version
tap-sunwave --help
tap-sunwave --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Swagger Schema

Here's where schemas are sourced from: https://emr.sunwavehealth.com/SunwaveEMR/swagger/swagger.json

### Contributing

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-sunwave` CLI interface directly using `poetry run`:

```bash
poetry run tap-sunwave --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-sunwave
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-sunwave --version
# OR run a test `elt` pipeline:
meltano run tap-sunwave target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

### Technical decisions

- pyscopg2 - keep Docker image size small by using `psycopg2-binary` rather adding edge repos for `postgresql17-contrib` and `postgresql17-dev`

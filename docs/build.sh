pandoc -s \
    -o ../web/static/docs.html \
    --css /static/docs.css \
    --metadata title="FlowKarma.Live Documentation" \
    fkl.md

FROM pretix/standalone:stable

COPY ./pretix_custom_fonts /tmp/pretix-custom-fonts

RUN pip3 install --no-cache-dir /tmp/pretix-custom-fonts

RUN cd /pretix && python3 -m pretix rebuild
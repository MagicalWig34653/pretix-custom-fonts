FROM pretix/standalone:stable

COPY ./pretix_custom_fonts /build/pretix_custom_fonts

RUN mkdir -p /tmp/pretix-custom-fonts \
    && cp -r /build/pretix_custom_fonts/* /tmp/pretix-custom-fonts/ \
    && pip3 install --no-cache-dir /tmp/pretix-custom-fonts \
    && rm -rf /tmp/pretix-custom-fonts

RUN cd /pretix && python3 -m pretix rebuild
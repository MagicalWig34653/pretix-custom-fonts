FROM pretix/standalone:stable

USER root

COPY ./pretix_custom_fonts /tmp/pretix-custom-fonts

RUN pip3 install --no-cache-dir /tmp/pretix-custom-fonts
RUN pip3 install --no-cache-dir pretix-fontpack-free

USER pretixuser

RUN cd /pretix && python3 -m pretix migrate && python3 -m pretix rebuild
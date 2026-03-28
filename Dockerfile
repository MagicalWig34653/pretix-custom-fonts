FROM pretix/standalone:stable

USER root

RUN apt update
RUN apt install -y ghostscript

COPY ./pretix_custom_fonts /build/pretix-custom-fonts

RUN pip3 install --no-cache-dir /build/pretix-custom-fonts
RUN pip3 install --no-cache-dir pretix-fontpack-free pretix-mandatory-product pretix-passbook pretix-zugferd

USER pretixuser

RUN cd /pretix && python3 -m pretix rebuild
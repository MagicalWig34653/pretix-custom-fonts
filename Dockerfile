FROM pretix/standalone:stable

# We switch to user pretix to ensure correct permissions
#USER pretix

# We copy the plugin code into the container
# Assuming the Dockerfile is in the project root (above pretix_custom_fonts directory)
COPY ./pretix_custom_fonts /pretix-custom-fonts


# Copy into a writable temp dir and install from there
RUN mkdir -p /tmp/pretix-custom-fonts \
    && cp -r /build/pretix_custom_fonts/* /tmp/pretix-custom-fonts/ \
    && pip3 install --no-cache-dir /tmp/pretix-custom-fonts \
    && rm -rf /tmp/pretix-custom-fonts /build/pretix_custom_fonts


# Rebuild pretix assets
RUN cd /pretix && python3 -m pretix rebuild

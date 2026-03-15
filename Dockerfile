FROM pretix/standalone:stable

# We switch to user pretix to ensure correct permissions
#USER pretix

# We copy the plugin code into the container
# Assuming the Dockerfile is in the project root (above pretix_custom_fonts directory)
COPY . /pretix-custom-fonts

# Install the plugin
RUN pip3 install --no-cache-dir /pretix-custom-fonts

# Run pretix build to collect static files and pre-compile translations
RUN cd /pretix && python3 -m pretix rebuild

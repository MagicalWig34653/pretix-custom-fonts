from setuptools import setup, find_packages


setup(
    name='pretix-custom-fonts',
    version='1.0.0',
    description='A pretix plugin to manage custom fonts for PDF output.',
    long_description='',
    url='https://github.com/your-username/pretix-custom-fonts',
    author='Junie',
    author_email='junie@jetbrains.com',
    license='Apache Software License',
    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points="""
[pretix.plugin]
pretix_custom_fonts=pretix_custom_fonts:PretixPluginMeta
""",
)

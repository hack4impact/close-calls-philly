require 'yaml'
require 'pathname'
require 'rspec/core/rake_task'
include FileUtils

namespace 'assets' do
    desc 'Updates the stylesheets generated by Sass'
    task :precompile do
      print %x(sass compile --time)
    end
end

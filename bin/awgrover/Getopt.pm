package awgrover::Getopt;
#use lib qw(../..);

use strict;
use awgrover::Report;

=head1 awgrover::Getopt

Like Getopt::Long, but supports "help", and returns a hashref 
(instead of binding to variables).

=head2 Usage

   my $switches=awgrover::Getopt::GetOptions
		(
		''=>'Tests the BDO UTC fix',
		'help|h|H'=>'this',
		'verbose|V:i'=>"[n]\tverbosity",
		'db=s'=>"oracle|mysql, the DB to use, see \%kConnectSets in this code",
		'create=s'=>"Issue create statements: [All], Table, Sequence",
		'drop=s'=>"Issue drop statements: [All], Table, Sequence",
		'test'=>'Do tests',
		'inhibit'=>'Inhibit the TZ fix',
		);

    $kVerbose = $switches->{'verbose'} || 1 if (defined $switches->{'verbose'});

	% ./BDO_UTC.pm -H
	BDO_utc.pm Tests the BDO UTC fix
        create=s        Issue create statements: [All], Table, Sequence
        db=s    oracle|mysql, the DB to use, see %kConnectSets in this code
        drop=s  Issue drop statements: [All], Table, Sequence
        help|h|H        this
        inhibit Inhibit the TZ fix
        test    Do tests
        verbose|V:i     [n]     verbosity

=head2 Configuration

=item $awgrover::Getopt::gExitOnHelp=1; # default

Exits the program, after displaying help, if any of the '-help' options are supplied.

=item $awgrover::Getopt::gUndefIfFail=1; # default = 0

Return undef if parsing of any option fails.
Otherwise, it returns all the switches that could be parsed.

=head2 Getopt (switch=>helpText)

Set $awgrover::Getopt::gUndefIfFail=1 if you want a parse to return undef if it fails. 

=over 4

=item ''=>'Command description'

The "empty" switch definition is purely help text displayed first.

=item 'help'=>'Displays the list of switches and descriptions'

Always assumed to be the 'help' switch, and must have the text 'help' 
Displays all the switch definitions and exits.

=item 'switchDefinition'=>'Description of switch'

A Getopt::Long style 'switchDefinition' and it's description. You can use 
aliases, etc, and the first alias is the canonical (and hash-key).

The returned hash will have the {canonicalSwitchName=>value} only if the switch
was supplied on the command line. For boolean switches, it will be 1.

Be careful using the optional forms, as they greedily consume arguments that 
you might not mean:

	'someInt:i'=>'will be greedy if it can'
	% command -someInt
	# switches->{'someInt'} == defined && 0
	% command -someInt 1
	# switches->{'someInt'} == 1, doesn't leave it in ARGV!
	% command -someInt A	
	# switches->{'someInt'} == defined && 0, leaves 'A' in ARGV.

Apparently allows abbreviations of the switch by default.
	
=back 4

=head2 Bugs

Pretty up the help so the columns align.

Allow any string for "help". It's hard-coded right now.

=cut

##########################################

use Verbose;
use Getopt::Long;
use File::Basename;

use vars qw($gUndefIfFail);
$gUndefIfFail=0;	# set to true to return UNDEF if can't parse
use vars qw($gExitOnHelp);
$gExitOnHelp=1;	# set to false to inhibit exiting on "-help"
use vars qw($gHelpOnFail);
$gHelpOnFail = 1;

no warnings 'redefine';
sub GetOptions(@)
	{
	use warnings 'redefine';
	# Give a list of switchDefinitions (from Getopt::Long),
	# Returns a hash whose keys are the extant switches,
	# and values are extant values
	my %switchDefinitions=@_;

	#vverbose 0,"in\n";
	
	my $helpFirstLine=delete $switchDefinitions{''};

	my %switch;

	# Getopt will put things in a hash for me (and do the right thing with @ and %)
	# # Getopt allows a function as the binding
	# # I'll use that to build the hash
	# # A nice side-effect is that Getopt does
	# # the parsing of the switchDefinition and
	# # gives me the true-name
	# 	my $builderFn = sub
	# 		{
	# 		my ($switchName, $switchValue)=@_;
	# 		$switch{$switchName}=$switchValue;
	# 		#print "switchname='$switchName'\n";
	# 		};
  # 
	# # Build an argument list for GetOptions
	# # It looks like this:
	# # switchDef,bindingAddress...
  # 
	# my @argList=map {($_,$builderFn)} keys %switchDefinitions;
  # 
	# #vverbose 0,"bult arglist\n";
	#
	# Getopt::Long::GetOptions(@argList);
	
	Getopt::Long::Configure ("bundling_override","posix_default","no_ignore_case");
	my $parsed = Getopt::Long::GetOptions(\%switch, keys %switchDefinitions); 
	if ($switch{'help'})
		{
		printSwitchHelp($helpFirstLine,%switchDefinitions);
		exit if $gExitOnHelp;
		}

        if (!$parsed) {
            print basename($0)." usage:\n";
            printSwitchHelp($helpFirstLine,%switchDefinitions) if $gHelpOnFail;
            return undef if ($gUndefIfFail);
            }
	
	return \%switch;
	}

sub GetCLI
	{
	# regenerate command line
	my ($switchHash, $switchDefinitions)=@_;
	
	my @switches;
	foreach my $switchDef (keys %$switchDefinitions)
		{
		my ($switchNames,$switchType)= split(/[=:]/,$switchDef);
		#vverbose 0,"$switchNames=>'$switchType'\n";
		my ($canonicalSwitchName)=split(/\|/,$switchNames);
		
		#vverbose 0,"$canonicalSwitchName=>'$switchType'\n";
		next if !exists($switchHash->{$canonicalSwitchName});
		
		my $value = $switchHash->{$canonicalSwitchName};
		#vverbose 0,"	=>'$value'\n";

		# Boolean has no value
		if (!$switchType)
			{
			next if !defined($switchHash->{$canonicalSwitchName}) 
				|| !$switchHash->{$canonicalSwitchName};
			$value='';
			}

		# Construct the switch=value
		else
			{
			# $value needs to be shell escaped!
			if (ref $value eq 'ARRAY')
				{
				if ($switchType =~ /\@/)
					{
					$value = "=".join(" -$canonicalSwitchName=",@$value);
					}
				else
					{
					$value = join(",",@$value);
					}
				}
			else
				{
				$value="=$value";
				}
			}
		
		push @switches,"-$canonicalSwitchName$value";	
		}
	return join(" ",@switches);
	}

sub printSwitchHelp
	{
	my $helpFirstLine=shift;
	my %switchDefinitions=@_;
	
	print $0," ",$helpFirstLine,"\n";
	my $switchDef;
	foreach $switchDef (sort keys %switchDefinitions)
		{
		awgrover::Report->PrintLine("   ","-".$switchDef,$switchDefinitions{$switchDef});
		}
	awgrover::Report->Flush;
	}

1;	

import React from 'react'
import Ribbon from './Ribbon.jsx'

class TeamContent extends React.Component {
  render() {
    const ribbonHtml = `        
    <span className='c-n-team-stat'>Wins: ${this.props.team.stats[0]}</span>
    <span className='c-n-team-stat'>Losses: ${this.props.team.stats[1]}</span>
    <span className='c-n-team-stat'>Ties: ${this.props.team.stats[2]}</span>  
    `
    const ribbonStyle = this.props.isDesktop ? {width: '50%', minWidth: '20rem', top: 0}: {width: '100%', top: 0}
    return(
      <div className='c-n-team'>
        <Ribbon html={ribbonHtml} 
            style={ribbonStyle}
            isDesktop={this.props.isDesktop} 
            primaryColor={this.props.team.colors[0]}/>
  
        {this.props.team.content.map((paragraph) => {
          return(<p>{paragraph}</p>)
        })}
      </div>
    )
  }

}

export default TeamContent